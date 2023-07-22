import logging
import os
import re
import subprocess
from abc import ABCMeta, abstractmethod

import pandas
from mypy_gpt.common import setup_logger

logger=logging.getLogger('linter')
logger.propagate=False



class Linter(metaclass=ABCMeta):
    @abstractmethod
    def run_checker(self, file, additional_args, program_path, proj_path):
        pass

    @staticmethod
    @abstractmethod
    def parse_line(line):
        pass

    def get_issues(self,args, override_file=None):

        out = self.run_checker(args.file if override_file is None else override_file, args.mypy_args, args.mypy_path,
                       args.proj_path)
        logger.info(out)
        issues = [self.parse_line(z) for z in out.split('\n')]
        issues = list(filter(lambda x: x, issues))
        if len(issues) == 0:
            return []
        # Here we unite the issues from different lines
        dfo = pandas.DataFrame(issues)
        changed_message_df = dfo.groupby('Line Number')['Message'].agg(lambda x: '\n'.join(x))
        df_first_row = dfo.groupby('Line Number').first()
        df_first_row['Message'].update(changed_message_df)
        df_first_row = df_first_row.reset_index()
        issues = [dict(r[1]) for r in df_first_row.iterrows()]

        if args.max_errors:
            issues = issues[:args.max_errors]
        if args.error_categories:
            issues = [z for z in issues if z['Category'] in args.error_categories.split(',')]
        return issues


class MyPyLinter(Linter):
    def __init__(self,debug):
        setup_logger(logger,debug) #for now
    def run_checker(self, file, additional_args, program_path, proj_path):
        # Construct the mypy command
        command = [program_path] + additional_args.split() + [file]
        logger.debug("Running mypy command: %s", command)
        # Run mypy command and capture the output
        result = subprocess.run(command, capture_output=True, text=True,cwd=os.path.abspath(proj_path))
        # Print the output

        # Decode the output from bytes to string
        output = result.stdout

        # 7-bit C1 ANSI sequences
        ansi_escape = re.compile(r'''
                \x1B  # ESC
                (?:   # 7-bit C1 Fe (except CSI)
                    [@-Z\\-_]
                |     # or [ for CSI, followed by a control sequence
                    \[
                    [0-?]*  # Parameter bytes
                    [ -/]*  # Intermediate bytes
                    [@-~]   # Final byte
                )
            ''', re.VERBOSE)
        result = ansi_escape.sub('', output)
        # Print the output
        return (result)
    @staticmethod
    def parse_line(line):
        import re
        # Extracting message, type, and line number using regular expressions
        pattern = r'(.+):(\d+): (\w+): (.+) \[(.*)\]'
        match = re.match(pattern, line)
        if not match:
            pattern = r'(.+):(\d+): (\w+): (.+)()'
            match = re.match(pattern, line)

        if match:
            linenumber = match.group(2)
            error_type = match.group(3)
            message = match.group(4)
            sub_type = match.group(5)
            return {"Line Number": linenumber, "Error Type": error_type, "Message": message, "Category": sub_type}
        else:
            logger.debug(("No match found.", line))
