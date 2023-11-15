    def add_module(self, req):
        for ext in ["py", "pyc"]:
            file_path = "{}.{}".format(req, ext)
            self.copier(self.system_stdlib / file_path, self.lib_dir / file_path)