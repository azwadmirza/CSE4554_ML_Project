    def get_paths(self):
        searched_path = '.'
        relative_path = 'dbt_project.yml'
        absolute_path = os.path.normcase(os.path.abspath(os.path.join(
            self.project.project_root, searched_path, relative_path
        )))
        path = FilePath(
            searched_path='.',
            relative_path='relative_path',
            absolute_path=absolute_path,
        )
        return [path]