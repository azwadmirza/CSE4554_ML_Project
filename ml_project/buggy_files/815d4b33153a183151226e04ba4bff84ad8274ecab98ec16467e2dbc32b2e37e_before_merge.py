    def wrapper(self, *args, **kwargs):
        try:
            res = func(self, *args, **kwargs)
            if res is None:
                res = True
        except SyncError as exc:
            file_name = os.path.basename(exc.dbx_path)
            logger.warning('Could not sync %s', file_name, exc_info=True)
            if exc.dbx_path is not None:
                if exc.local_path is None:
                    exc.local_path = self.to_local_path(exc.dbx_path)
                self.sync_errors.put(exc)
                if any(isinstance(a, Metadata) for a in args):
                    self.download_errors.add(exc.dbx_path)

            res = False

        return res