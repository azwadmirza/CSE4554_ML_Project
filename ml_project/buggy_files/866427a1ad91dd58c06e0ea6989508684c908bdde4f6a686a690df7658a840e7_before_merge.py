    def __iter__(self) -> Iterator[FilePath]:
        ext = "[!.#~]*" + self.extension

        root = self.project.project_root

        for result in find_matching(root, self.relative_dirs, ext):
            file_match = FilePath(**{
                k: os.path.normcase(v) for k, v in result.items()
            })
            yield file_match