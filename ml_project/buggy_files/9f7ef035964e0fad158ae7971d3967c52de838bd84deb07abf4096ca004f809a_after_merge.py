    def method_call(self, method_name, args, kwargs):
        try:
            fn = getattr(self.held_object, method_name)
        except AttributeError:
            raise InvalidArguments('Module %s does not have method %s.' % (self.modname, method_name))
        if method_name.startswith('_'):
            raise InvalidArguments('Function {!r} in module {!r} is private.'.format(method_name, self.modname))
        if not getattr(fn, 'no-args-flattening', False):
            args = flatten(args)
        # This is not 100% reliable but we can't use hash()
        # because the Build object contains dicts and lists.
        num_targets = len(self.interpreter.build.targets)
        state = ModuleState(
            build_to_src=mesonlib.relpath(self.interpreter.environment.get_source_dir(),
                                          self.interpreter.environment.get_build_dir()),
            subproject=self.interpreter.subproject,
            subdir=self.interpreter.subdir,
            current_lineno=self.interpreter.current_lineno,
            environment=self.interpreter.environment,
            project_name=self.interpreter.build.project_name,
            project_version=self.interpreter.build.dep_manifest[self.interpreter.active_projectname],
            # The backend object is under-used right now, but we will need it:
            # https://github.com/mesonbuild/meson/issues/1419
            backend=self.interpreter.backend,
            compilers=self.interpreter.build.compilers,
            targets=self.interpreter.build.targets,
            data=self.interpreter.build.data,
            headers=self.interpreter.build.get_headers(),
            man=self.interpreter.build.get_man(),
            global_args=self.interpreter.build.global_args,
            project_args=self.interpreter.build.projects_args.get(self.interpreter.subproject, {}),
            build_machine=self.interpreter.builtin['build_machine'].held_object,
            host_machine=self.interpreter.builtin['host_machine'].held_object,
            target_machine=self.interpreter.builtin['target_machine'].held_object,
        )
        if self.held_object.is_snippet(method_name):
            value = fn(self.interpreter, state, args, kwargs)
            return self.interpreter.holderify(value)
        else:
            value = fn(state, args, kwargs)
            if num_targets != len(self.interpreter.build.targets):
                raise InterpreterException('Extension module altered internal state illegally.')
            return self.interpreter.module_method_callback(value)