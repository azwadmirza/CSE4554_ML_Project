    def check(self):
        dag_folder = conf.get("core", "dags_folder")
        file_paths = list_py_file_paths(directory=dag_folder, include_examples=False)
        problems = []
        for file_path in file_paths:
            if not file_path.endswith(".py"):
                continue
            problems.extend(self._check_file(file_path))
        return problems