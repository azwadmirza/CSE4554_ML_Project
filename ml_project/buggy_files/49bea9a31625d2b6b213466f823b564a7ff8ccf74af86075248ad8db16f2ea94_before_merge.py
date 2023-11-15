    def get_default_state_dir(home_dir_postfix=u'.Tribler'):
        """Get the default application state directory."""
        state_directory_variable = u'${TSTATEDIR}'
        state_directory = os.path.expandvars(state_directory_variable)
        if state_directory and state_directory != state_directory_variable:
            return state_directory

        if os.path.isdir(home_dir_postfix):
            return os.path.abspath(home_dir_postfix)

        application_directory = get_appstate_dir()
        return os.path.join(application_directory, home_dir_postfix)