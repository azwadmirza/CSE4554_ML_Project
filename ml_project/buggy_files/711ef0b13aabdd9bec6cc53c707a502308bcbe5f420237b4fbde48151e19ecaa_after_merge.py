    def _find_source_script(self, name, args):
        # Prefer scripts in the current source directory
        search_dir = os.path.join(self.interpreter.environment.source_dir,
                                  self.interpreter.subdir)
        key = (name, search_dir)
        if key in self._found_source_scripts:
            found = self._found_source_scripts[key]
        else:
            found = dependencies.ExternalProgram(name, search_dir=search_dir)
            if found.found():
                self._found_source_scripts[key] = found
            else:
                raise InterpreterException('Script {!r} not found'.format(name))
        return build.RunScript(found.get_command(), args)