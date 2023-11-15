    def handle(self, *args, **options):
        if options[self.subcommand_dest] in self.instances:
            command = self.instances[options[self.subcommand_dest]]
            if options.get('no_color'):
                command.style = no_style()
                command.stderr.style_func = None
            if options.get('stdout'):
                command.stdout = OutputWrapper(options['stdout'])
            if options.get('stderr'):
                command.stderr = OutputWrapper(options.get('stderr'), command.stderr.style_func)
            command.handle(*args, **options)
        else:
            self.print_help('manage.py', 'cms')