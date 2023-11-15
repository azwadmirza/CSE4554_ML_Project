    def first_python_binary() -> Optional[str]:
        for binary_paths in all_python_binary_paths:
            if binary_paths.first_path:
                return binary_paths.first_path.path
        return None