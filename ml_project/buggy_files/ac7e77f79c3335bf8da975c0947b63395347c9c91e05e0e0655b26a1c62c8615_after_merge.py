    def __init__(self, command):
        build_commands = {
            'build',
            'convert',
            'develop',
            'index',
            'inspect',
            'metapackage',
            'render',
            'skeleton',
        }
        needs_source = {
            'activate',
            'deactivate'
        }
        if command in build_commands:
            message = dals("""
            You need to install conda-build in order to
            use the 'conda %(command)s' command.
            """)
        elif command in needs_source and not on_win:
            message = dals("""
            '%(command)s is not a conda command.
            Did you mean 'source %(command)s'?
            """)
        else:
            message = "Conda could not find the command: '%(command)s'"
        super(CommandNotFoundError, self).__init__(message, command=command)