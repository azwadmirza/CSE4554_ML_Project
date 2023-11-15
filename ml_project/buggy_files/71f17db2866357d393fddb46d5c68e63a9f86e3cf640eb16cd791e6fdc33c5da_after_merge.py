    def run(self, cmd, **kwargs):
        self._create_path_if_not_exists()
        replaced_cmd = [
            part.replace('{prefix}', self.prefix_dir) for part in cmd
        ]
        return cmd_output(*replaced_cmd, __popen=self.__popen, **kwargs)