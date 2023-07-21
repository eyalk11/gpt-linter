# mypy-gpt
Solve mypy errors using [guidance](https://github.com/microsoft/guidance) and gpt API.
It runs mypy on targeted file and then uses gpt to try to fix the issues (espcially good for minor nagging issues).
Displays a diff file for the required changes and ask you if you want to apply. 

# Installation
```
pip install  mypy-gpt

```
it is generally better to install the master 

```
pip install git+https://github.com/eyalk11/mypy-gpt.git
```

You will need openai access token for it. 

In powershell:
```
$env:OPEN_AI_KEY = "sk-XXX"
```
Or 
```
OPEN_AI_KEY=sk-XXX python -m mypy_gpt ...
```


# Usage
See 
```
python -m mypy_gpt --help 
```

A typical usage is 
```
python -m mypy_gpt --proj-path [PROJECT] [PYFILE]
```
It then tries to get a list of fixes from the chat , prints them , and finally try to come up with an updated version of the solution. 
It then checks the final file again , showing you the errors after the change, and displayes a diff file. It asks you if you want to apply the changes, 
and reruns main if not all issues were resolved. 

If you want it to generate diff file, use: 

```
python -m mypy_gpt --proj-path [PROJECT] --dont-ask  [PYFILE] > myfile.diff (if you don't mind colors)
```
or 
```
python -m mypy_gpt --store-diff --proj-path [PROJECT] [PYFILE] --dont-ask
```
(it stores by default suggestion.diff)



For example: 

![image](https://github.com/eyalk11/mypy-gpt/assets/72234965/6b07e20f-2c9b-411b-b294-3f47a639c4d8)



