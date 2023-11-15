    def __iter__(self) -> Iterator[FilePath]:
        ext = "[!.#~]*" + self.extension

        root = self.project.project_root

        for result in find_matching(root, self.relative_dirs, ext):
            if 'searched_path' not in result or 'relative_path' not in result:
                raise InternalException(
                    'Invalid result from find_matching: {}'.format(result)
                )
            file_match = FilePath(
                searched_path=result['searched_path'],
                relative_path=result['relative_path'],
                project_root=root,
            )
            yield file_match