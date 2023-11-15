    def run_module(self):
        import runpy
        code = "run_module(modname, alter_sys=True)"
        global_dict = {
            "run_module": runpy.run_module,
            "modname": self.options.module
        }
        sys.argv = [self.options.module] + self.command[:]
        sys.path.append(os.getcwd())
        return self.run_code(code, global_dict)