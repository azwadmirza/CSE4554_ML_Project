    def run(self, cmd, **kwargs):
        self._create_path_if_not_exists()
        replaced_cmd = _replace_cmd(cmd, prefix=self.prefix_dir)
        return cmd_output(*replaced_cmd, __popen=self.__popen, **kwargs)