    def walk_docs_dir(self, docs_dir):
        for (dirpath, _, filenames) in os.walk(docs_dir):
            for filename in sorted(filenames):
                fullpath = os.path.join(dirpath, filename)
                relpath = os.path.normpath(os.path.relpath(fullpath, docs_dir))
                if self.file_match(relpath):
                    yield relpath