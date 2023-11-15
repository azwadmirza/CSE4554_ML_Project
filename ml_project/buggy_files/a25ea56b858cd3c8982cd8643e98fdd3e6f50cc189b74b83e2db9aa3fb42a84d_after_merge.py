        def cat2relpath(cat):
            # type: (CatalogInfo) -> unicode
            return relpath(cat.mo_path, self.env.srcdir).replace(path.sep, SEP)