import os

import guidance


class Guidance:

    @staticmethod
    def guide_for_errors(args):
        guidance.llm = guidance.llms.OpenAI(args.model, api_key=os.environ['OPEN_AI_KEY'])

        return  guidance('''
    {{#system~}}
        You are a helpful assistant. You will be given a file and an issue. You need to come up with fixes for the issue, even if it is a minor issue.
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
        Be short and preicise regarding the fix. Describe the change in the code but do not repeat much code.
      {{~/user}}
      {{#assistant~}}
        {{gen 'fix' list_append=True temperature=0.7 max_tokens=%d}}
        {{~/assistant}}
        
    {{/each~}}''' % (args.max_tokens_per_fix), log=True,caching=False)

    @staticmethod
    def guide_for_fixes(args):
        return guidance('''
            {{#system~}}
            You are a helpful assistant. You will be given a list of corrections to do in a file, and will update the file accordingly. 
            Reply only with xml that has the following format:  
            ```xml
            <pythonfile>the updated file content after the corrections are made</pythonfile>
            ```
            {{~/system}}
            {{#user~}}
            This is the file:
            {{file}}
            Those are the fixes
            {{#each fixes}}- {{this}}
                {{/each~}}
    
            {{~/user}}
    
            {{#assistant~}}
            {{gen 'fixedfile' temperature=0.2 max_tokens=%d}}
            {{~/assistant~}}
        ''' % (args.max_tokens_for_file),log=True ,caching=False)
