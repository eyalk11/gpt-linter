# gpt-linter
Solve linter errors using [guidance](https://github.com/microsoft/guidance) and gpt API.
It runs mypy on targeted file and then uses gpt to try to fix the issues (espcially good for minor nagging issues).
Displays a diff file for the required changes and ask you if you want to apply. 

# Installation
```
pip install  gpt-linter

```
it is generally better to install the master 

```
pip install git+https://github.com/eyalk11/gpt-linter.git
```

You will need openai access token for it. 

In powershell:
```
$env:OPEN_AI_KEY = "sk-XXX"
```
Or 
```
OPEN_AI_KEY=sk-XXX python -m gpt_linter ...
```

Of course, mypy is required too. 


# Usage
See 
```
python -m gpt_linter --help 
```

A typical usage is 
```
python -m gpt_linter --proj-path [PROJECT] [PYFILE]
```
It then tries to get a list of fixes from the chat , prints them , and finally try to come up with an updated version of the solution. 
It then checks the final file again , showing you the errors after the change, and displayes a diff file. It asks you if you want to apply the changes, 
and reruns main if not all issues were resolved. 

If you want it to generate diff file, use: 

```
python -m gpt_linter --proj-path [PROJECT] --no-color --dont-ask  [PYFILE] > myfile.diff 
```



For example: 
![image](https://github.com/eyalk11/gpt-linter/assets/72234965/ed4eebb2-b4a5-4cc5-ad02-4e2299a1ec20)


