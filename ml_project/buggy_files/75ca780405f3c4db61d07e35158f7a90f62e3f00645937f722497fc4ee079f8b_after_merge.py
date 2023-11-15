    def replacements(self, creator, dest_folder):
        return {
            "__VIRTUAL_PROMPT__": "" if self.flag_prompt is None else self.flag_prompt,
            "__VIRTUAL_ENV__": six.ensure_text(str(creator.dest_dir)),
            "__VIRTUAL_NAME__": creator.env_name,
            "__BIN_NAME__": six.ensure_text(str(creator.bin_dir.relative_to(creator.dest_dir))),
            "__PATH_SEP__": os.pathsep,
        }