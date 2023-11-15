    def get_paths(self) -> List[FilePath]:
        path = FilePath(
            project_root=self.project.project_root,
            searched_path='.',
            relative_path='dbt_project.yml',
        )
        return [path]