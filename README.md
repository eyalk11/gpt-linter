# mypy-gpt
Solve mypy errors using guidance and chatgpt!
# Usage

```
usage: main.py [-h] [--mypy_path MYPY_PATH] [--error_categories ERROR_CATEGORIES] [--max_errors MAX_ERRORS] [--proj-path PROJ_PATH] [--diff_file DIFF_FILE] [--new_file_path NEW_FILE_PATH]
               [--store_file] [--store_diff] [--dont_ask] [--model MODEL] [--max_fixes_tokens MAX_FIXES_TOKENS] [--max_file_tokens MAX_FILE_TOKENS]
               file [mypy_args]

Run mypy on a Python file

positional arguments:
  file                  Python file to run mypy on
  mypy_args             Additional options for mypy

optional arguments:
  -h, --help            show this help message and exit
  --mypy_path MYPY_PATH
                        Path to mypy executable (default: "mypy")
  --error_categories ERROR_CATEGORIES
                        Type of errors to process
  --max_errors MAX_ERRORS
                        Max number of errors to process
  --proj-path PROJ_PATH
                        Path to project
  --diff_file DIFF_FILE
                        Store diff in file
  --new_file_path NEW_FILE_PATH
                        Store new content in file
  --store_file          Store new content in file
  --store_diff          Store diff in a file
  --dont_ask            Store new content in file
  --model MODEL         Openai model to use
  --max_fixes_tokens MAX_FIXES_TOKENS
                        tokens to use for fixes
  --max_file_tokens MAX_FILE_TOKENS
                        tokens to use for file

```

(see main.py for an updated version)


