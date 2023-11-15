    def first_python_binary() -> Optional[PythonExecutable]:
        for binary_paths in all_python_binary_paths:
            if binary_paths.first_path:
                return PythonExecutable(
                    path=binary_paths.first_path.path,
                    fingerprint=binary_paths.first_path.fingerprint,
                )
        return None