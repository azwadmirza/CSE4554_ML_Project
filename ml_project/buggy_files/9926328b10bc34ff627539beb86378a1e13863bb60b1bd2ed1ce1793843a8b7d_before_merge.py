    def build_search_paths(cls, config, user_subdir: Optional[str] = None,
                           extra_dir: Optional[str] = None) -> List[Path]:

        abs_paths: List[Path] = [cls.initial_search_path]

        if user_subdir:
            abs_paths.insert(0, config['user_data_dir'].joinpath(user_subdir))

        if extra_dir:
            # Add extra directory to the top of the search paths
            abs_paths.insert(0, Path(extra_dir).resolve())

        return abs_paths