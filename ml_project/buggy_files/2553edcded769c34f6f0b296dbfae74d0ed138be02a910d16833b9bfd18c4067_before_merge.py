    def is_venv_in_project(self):
        return (
            PIPENV_VENV_IN_PROJECT or
            os.path.exists(os.path.join(self.project_directory, '.venv'))
        )