    def get_default_state_dir(home_dir_postfix=u'.Tribler'):
        """Get the default application state directory."""
        if 'TSTATEDIR' in os.environ:
            return os.environ['TSTATEDIR']

        if os.path.isdir(home_dir_postfix):
            return os.path.abspath(home_dir_postfix)

        application_directory = get_appstate_dir()
        return os.path.join(application_directory, home_dir_postfix)