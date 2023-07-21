# mypy-gpt
Solve mypy errors using [guidance](https://github.com/microsoft/guidance) and espcially chatgpt.
It runs mypy on targeted file and then uses gpt to try to fix the issues (espcially good for minor nagging issues).
Displays a diff file for the required changes and ask you if you want to apply. 

# Installation
```
pip install  mypy-gpt
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
(see main.py for a generally more updated version of usage)

If you want it to generate diff file, use: 

```
python -m mypy_gpt --proj-path [PROJECT] [PYFILE] --dont-ask > myfile.diff
```


For example: 

![image](https://github.com/eyalk11/mypy-gpt/assets/72234965/6b07e20f-2c9b-411b-b294-3f47a639c4d8)



