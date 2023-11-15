    def _load_vars_prompt(self, attr, ds):
        new_ds = preprocess_vars(ds)
        vars_prompts = []
        if new_ds is not None:
            for prompt_data in new_ds:
                if 'name' not in prompt_data:
                    display.deprecated("Using the 'short form' for vars_prompt has been deprecated", version="2.7")
                    for vname, prompt in prompt_data.items():
                        vars_prompts.append(dict(
                            name=vname,
                            prompt=prompt,
                            default=None,
                            private=None,
                            confirm=None,
                            encrypt=None,
                            salt_size=None,
                            salt=None,
                        ))
                else:
                    vars_prompts.append(prompt_data)
        return vars_prompts