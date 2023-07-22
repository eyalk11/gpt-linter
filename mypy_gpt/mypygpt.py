
import os
import xml

import logging
import xml.etree.ElementTree as ET

from mypy_gpt.common import setup_logger, generate_diff
from mypy_gpt.guide import Guidance
from mypy_gpt.linter import MyPyLinter

logger=logging.getLogger('mypygpt')
logger.propagate=False

DEFAULT_MODEL = "gpt-3.5-turbo-16k"

MYPYARGS = '--disallow-untyped-defs'

older_path = r"c:\gitproj\Auto-GPT"
DEFAULT_TOKENS =3600
DEFAULT_TOKENS_PER_FIX =400
import argparse


class MyPyGpt:
    def __init__(self,args):
        #move all the attributes of args to local variables
        self.args = args
        self.file = args.file
        self.original_content = open(self.file, 'rt').read()

        self.debug = args.debug
        self.linter = MyPyLinter(args.debug)

    def get_new_content(self,err_res):
        fix_guide= Guidance.guide_for_fixes(self.args)
        fix_res=fix_guide(filename=self.file, file=self.original_content, fixes=err_res['fix'])
        if not 'fixedfile' in fix_res:
            logger.error('no fixed file')
            return None
        fixed = fix_res['fixedfile']
        logger.debug(f'fixed file: {fixed}')
        #bb = json.loads(fix_res["fixedfile"])['pythonfile']
        try:
            new_content= fixed[fixed.index('```xml') + 6:]
            new_content=new_content[:new_content.rindex('```')]
        except:
            if len(fixed)>0.5*len(self.original_content):
                new_content=fixed
            else:
                return None
        try:
            new_content=ET.fromstring(new_content).text #remove the pythonfile element

        except xml.etree.ElementTree.ParseError:
            logger.error("bad formatting")
            logger.debug(new_content)
            if len(fixed) > 0.5 * len(self.original_content):
                logger.warn("will try anyway")
            else:
                return None

        return new_content

    def get_issues_string(self,issues):
        for issue in issues:
            ln=int(issue['Line Number'])
            lines=self.original_content.split('\n')
            lines= '\n'.join(lines[ max(ln-1-5,0) :min(ln-1+5,len(lines))])
            issue[f"context(lines {ln-5} to {ln+5})"]=lines

            st='\n'.join(f"{k}: {v}" for k,v in issue.items())

            logger.debug(st)
            yield st

    def main(self):
        setup_logger(logger,self.debug)

        if 'OPEN_AI_KEY' not in os.environ:
            logger.error('OPEN_AI_KEY not set')
            return
        Guidance.set_key(self.args)
        logger.info("mypy output:")

        errors = self.linter.get_issues(self.args)
        logger.debug(errors)
        if len(errors)==0:
            logger.info('no errors')
            return

        err_res = self.get_fixes(list(self.get_issues_string(errors)))
        new_content=self.get_new_content(err_res)
        if new_content is None:
            logger.error('cant continue')
            return


        colored_diff,diff= generate_diff(self.original_content, new_content, self.args.file.replace("\\", '/'))

        if self.args.diff_file:
            open(self.args.diff_file, 'wt').write(diff)

        if not self.args.dont_recheck:
            errors = self.check_new_file(new_content)

        print(colored_diff)
        update=False

        if not self.args.dont_ask:
            print("do you want to override the file? (y/n)")
            if input() == 'y':
                update=True

        if (len(errors) == 0 and self.args.auto_update)  or update:
            open(self.args.file, 'wt').write(new_content)
            if not self.args.dont_recheck and len(errors) >0 :
                self.main()

    def check_new_file(self, new_content):
        newfile = self.args.file.replace('.py', '.fixed.py')  # must be in the same folder sadly.
        open(newfile, 'wt').write(new_content)
        logger.info('output from mypy after applying the fixes:')
        try:
            return self.linter.get_issues(self.args, override_file=newfile)
        finally:
            if not self.args.store_fixed_file:
                try:
                    os.remove(newfile)
                except:
                    logger.error('could not remove file %s' % newfile)


    def get_fixes(self, errors):
        err_guide = Guidance.guide_for_errors(self.args)
        err_res = err_guide(filename=self.file, file=self.original_content, errors=errors)
        if not self.args.dont_print_fixes:
            logger.info('suggested fixes:')
            logger.info('\n'.join(err_res['fix']))
        return err_res


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Run mypy on a Python file and use OpenAI GPT to fix the errors. It temporary generates file.fixed.py file to check for errors.')
    # Add the arguments
    parser.add_argument('file', help='Python file to run mypy on')
    parser.add_argument('mypy_args', nargs='?', default=MYPYARGS, help='Additional options for mypy')
    parser.add_argument('--mypy-path', default='mypy', help='Path to mypy executable (default: "mypy")')
    parser.add_argument('--error_categories', action='store', help='Type of errors to process')
    parser.add_argument('--max_errors', action='store', type=int, default=10, help='Max number of errors to process')
    parser.add_argument('--proj-path', default='.', help='Path to project')
    parser.add_argument('--diff-file', action='store', help='Store diff in diff file')
    parser.add_argument('--store-fixed-file', action='store_true', default=False, help='Keeps file.fixed.py')

    parser.add_argument('--dont-ask', action='store_true', default=False,
                        help='Dont ask if to apply to changes. Useful for generting diff')
    parser.add_argument('--model', default=DEFAULT_MODEL, help='Openai model to use')
    parser.add_argument('--max_tokens_per_fix', default=DEFAULT_TOKENS_PER_FIX, help='tokens to use for fixes')
    parser.add_argument('--max_tokens_for_file', default=DEFAULT_TOKENS, help='tokens to use for file')
    parser.add_argument('--dont_recheck', action='store_true', default=False,
                        help='Dont recheck the file after the fixes')
    parser.add_argument('--debug', action='store_true', default=False, help='debug log level ')
    parser.add_argument('--auto-update', action='store_true', default=False, help='auto update if no errors ')
    parser.add_argument('--dont-print-fixes', action='store_true', default=False, help='dont print fixes ')

    # Parse the arguments
    args = parser.parse_args()
    MyPyGpt(args).main()





if __name__ == '__main__':
    main()
