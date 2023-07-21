# This is a sample Python script.
import os

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import guidance
import re
import difflib

DEFAULT_MODEL = "gpt-3.5-turbo-16k"

MYPYARGS = '--disallow-untyped-defs'

older_path = r"c:\gitproj\Auto-GPT"
DEFAULT_TOKENS =3600
DEFAULT_TOKENS_PER_FIX =400
import subprocess

import argparse
def run_mypy(file, mypy_args, mypy_path,proj_path):
    # Construct the mypy command
    command = [mypy_path] +mypy_args.split() + [file]
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

def parse_line(line):
    import re
    # Extracting message, type, and line number using regular expressions
    pattern = r'(.+):(\d+): (\w+): (.+) \[(.*)\]'
    match = re.match(pattern, line)
    #if not match:
    #    pattern = r'(.+):(\d+): (\w+): (.+)()'
    #    match = re.match(pattern, line)

    if match:
        filename = match.group(1)
        linenumber = match.group(2)
        error_type = match.group(3)
        message = match.group(4)
        sub_type = match.group(5)
        return {"Line Number": linenumber, "Error Type": error_type, "Message": message, "Sub": sub_type}
    else:
        print("No match found.", line)

def guide_for_errors(args):
    guidance.llm = guidance.llms.OpenAI(DEFAULT_MODEL, api_key=os.environ['OPEN_AI_KEY'])

    return  guidance('''
{{#system~}}
    You are a helpful assistant. You will be given a file and a list of issues. Some of them are minor issues like mismatch types.  You need to come up with fixes for all issues, evem the minor ones.
    The fixes should be meticulously phrased. 
    {{~/system}}
{{~#user}}
Given this {{filename}}: .
        {{file}}.
A list of issues will be given
{{~/user}}

{{#each errors}}
  {{~#user}}
  What is the fix for this issue on {{filename}}?
          {{this}}
  {{~/user}}
  {{#assistant~}}
    {{gen 'fix' list_append=True temperature=0.7 max_tokens=%d}}
    {{~/assistant}}
    
{{/each~}}''' % (args.max_tokens_per_fix), log=True)

def guide_for_fixes(args): 
    return guidance('''
        {{#system~}}
        You are a helpful assistant. You will be given a list of corrections to do in a file, and will update the file accordingly. Reply only with the full file content after the changes are applied. 
        {{~/system}}
        {{#user~}}
        This is the file {{file}}
        Those are the fixes
        {{#each fixes}}- {{this}}
            {{/each~}}

        {{~/user}}

        {{#assistant~}}
        {{gen 'fixedfile' temperature=0.7 max_tokens=%d}}
        {{~/assistant~}}
    ''' % (args.max_tokens_for_file),log=True )


def generate_diff(original_content, new_content,path):
    try:
        from colorama import Fore, Back, Style, init
        init()
    except ImportError:  # fallback so that the imported classes always exist
        class ColorFallback():
            __getattr__ = lambda self, name: ''

        Fore = Back = Style = ColorFallback()

    def color_diff(diff):
        for line in diff:
            if line.startswith('+'):
                yield Fore.GREEN + line + Fore.RESET
            elif line.startswith('-'):
                yield Fore.RED + line + Fore.RESET
            elif line.startswith('^'):
                yield Fore.BLUE + line + Fore.RESET
            elif line.startswith('@@'):
                yield Fore.BLUE + line[:line.rindex('@@')+2] + Fore.RESET
            else:
                yield line

    diffres =difflib.unified_diff(original_content.split('\n'), new_content.split('\n'), fromfile=path, tofile=path+"b")
    return '\n'.join(color_diff(diffres)),'\n'.join(diffres)

def main(args):
    out=run_mypy(args.file, args.mypy_args, args.mypy_path, args.proj_path)
    print(out)

    errors = [parse_line(z) for z in out.split('\n')]
    errors =list(filter(lambda x:x,errors))
    if args.max_errors:
        errors = errors[:args.max_errors]
    if args.error_categories:
        errors = [z for z in errors if z['Category'] in args.error_categories.split(',')]
    if len(errors)==0:
        print('no errors')
        return

    err_guide=guide_for_errors(args)
    original_content=open(args.file, 'rt').read()

    err_res = err_guide(filename=args.file, file=original_content, errors=errors)

    print('suggested fixes:')
    print('\n'.join(err_res['fix']))
    fix_guide=guide_for_fixes(args)
    fix_res=fix_guide(filename=args.file, file=original_content, errors=errors, fixes=err_res['fix'])
    if 'fixedfile' in fix_res:
        fixed = fix_res['fixedfile']
        try:
            new_content=fixed[fixed.index('```python') + 9:fixed.rindex('```')]
        except:
            print('failed parsing resp')
            if len(fixed)>0.5*len(original_content):
                new_content=fixed
            else:
                print(fix_res['fixedfile'])
                print('cant continue')
                return
        colored_diff,diff= generate_diff(original_content, new_content,args.file.replace("\\",'/'))
        print(colored_diff)
        if args.store_file:
            open(args.new_file_path, 'wt').write(new_content)
        if args.store_diff:
            open(args.diff_file_path, 'wt').write(diff)

        if not args.dont_ask:
            print("do you want to override the file? (y/n)")
            if input() == 'y':
                open(args.file, 'wt').write(new_content)
                print('situation after applying the fixes:')
                if not args.dont_recheck:
                    main(args)



if __name__ == '__main__':
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Run mypy on a Python file')
    # Add the arguments
    parser.add_argument('file', help='Python file to run mypy on')
    parser.add_argument('mypy_args', nargs='?', default=MYPYARGS, help='Additional options for mypy')
    parser.add_argument('--mypy_path', default='mypy', help='Path to mypy executable (default: "mypy")')
    parser.add_argument('--error_categories', action='store', help='Type of errors to process')
    parser.add_argument('--max_errors', action='store',type=int,default=10, help='Max number of errors to process')
    parser.add_argument('--proj-path', default='.', help='Path to project')
    parser.add_argument('--diff_file', action='store',default='suggestion.diff', help='Store diff in file')
    parser.add_argument('--new_file_path', action='store',default='suggestion.py', help='Store new content in file')
    parser.add_argument('--store_file', action='store_true',default=False, help='Store new content in file')
    parser.add_argument('--store_diff', action='store_true',default=False, help='Store diff in a file')

    parser.add_argument('--dont_ask', action='store_true', default=False, help='Store new content in file')
    parser.add_argument('--model', default=DEFAULT_MODEL,help ='Openai model to use')
    parser.add_argument('--max_tokens_per_fix', default=DEFAULT_TOKENS_PER_FIX, help='tokens to use for fixes')
    parser.add_argument('--max_tokens_for_file', default=DEFAULT_TOKENS,  help='tokens to use for file')
    parser.add_argument('--dont_recheck', action='store_true', default=False, help='Dont recheck the file after the fixes')
    # Parse the arguments
    args = parser.parse_args()
    main(args)


