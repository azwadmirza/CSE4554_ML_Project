        def cat2relpath(cat):
            # type: (CatalogInfo) -> unicode
            return path.relpath(cat.mo_path, self.env.srcdir).replace(path.sep, SEP)