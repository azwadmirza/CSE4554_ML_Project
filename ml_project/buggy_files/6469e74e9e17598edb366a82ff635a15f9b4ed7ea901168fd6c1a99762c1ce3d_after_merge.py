    def walk_docs_dir(self, docs_dir):

        if self.file_match is None:
            raise StopIteration

        for (dirpath, dirs, filenames) in os.walk(docs_dir):
            dirs.sort()
            for filename in sorted(filenames):
                fullpath = os.path.join(dirpath, filename)

                # Some editors (namely Emacs) will create temporary symlinks
                # for internal magic. We can just ignore these files.
                if os.path.islink(fullpath):
                    fp = os.path.join(dirpath, os.readlink(fullpath))
                    if not os.path.exists(fp):
                        continue

                relpath = os.path.normpath(os.path.relpath(fullpath, docs_dir))
                if self.file_match(relpath):
                    yield relpath