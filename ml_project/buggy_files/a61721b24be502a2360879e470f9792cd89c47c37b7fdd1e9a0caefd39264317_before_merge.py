    def _update_prompt(self, set_vars, conda_prompt_modifier):
        if not context.changeps1:
            return

        if self.shell == 'posix':
            ps1 = os.environ.get('PS1', '')
            current_prompt_modifier = os.environ.get('CONDA_PROMPT_MODIFIER')
            if current_prompt_modifier:
                ps1 = re.sub(re.escape(current_prompt_modifier), r'', ps1)
            # Because we're using single-quotes to set shell variables, we need to handle the
            # proper escaping of single quotes that are already part of the string.
            # Best solution appears to be https://stackoverflow.com/a/1250279
            ps1 = ps1.replace("'", "'\"'\"'")
            set_vars.update({
                'PS1': conda_prompt_modifier + ps1,
            })
        elif self.shell == 'csh':
            prompt = os.environ.get('prompt', '')
            current_prompt_modifier = os.environ.get('CONDA_PROMPT_MODIFIER')
            if current_prompt_modifier:
                prompt = re.sub(re.escape(current_prompt_modifier), r'', prompt)
            set_vars.update({
                'prompt': conda_prompt_modifier + prompt,
            })