    def get_staticfiles_finders(self):
        """
        Returns a sorted mapping between the finder path and the list
        of relative and file system paths which that finder was able
        to find.
        """
        finders_mapping = OrderedDict()
        for finder in finders.get_finders():
            for path, finder_storage in finder.list([]):
                if getattr(finder_storage, "prefix", None):
                    prefixed_path = join(finder_storage.prefix, path)
                else:
                    prefixed_path = path
                finder_cls = finder.__class__
                finder_path = ".".join([finder_cls.__module__, finder_cls.__name__])
                real_path = finder_storage.path(path)
                payload = (prefixed_path, real_path)
                finders_mapping.setdefault(finder_path, []).append(payload)
                self.num_found += 1
        return finders_mapping