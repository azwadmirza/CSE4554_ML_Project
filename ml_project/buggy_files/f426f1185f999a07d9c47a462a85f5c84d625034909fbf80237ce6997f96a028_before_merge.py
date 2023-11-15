    def post_process_args(self, options, args):
        options, args = super(DocCLI, self).post_process_args(options, args)

        if [options.all_plugins, options.json_dump, options.list_dir, options.list_files, options.show_snippet].count(True) > 1:
            raise AnsibleOptionsError("Only one of -l, -F, -s, -j or -a can be used at the same time.")

        display.verbosity = options.verbosity

        # process all plugins of type
        if options.all_plugins:
            args = self.get_all_plugins_of_type(options['type'])
            if options.module_path:
                display.warning('Ignoring "--module-path/-M" option as "--all/-a" only displays builtins')

        return options, args