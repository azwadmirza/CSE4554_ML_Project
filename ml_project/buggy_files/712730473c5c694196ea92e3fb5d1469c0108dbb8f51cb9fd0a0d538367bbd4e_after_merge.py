def catch_sync_issues(download=False):
    """
    Returns a decorator that catches all SyncErrors and logs them.
    Should only be used for methods of UpDownSync.
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                res = func(self, *args, **kwargs)
                if res is None:
                    res = True
            except SyncError as exc:
                # fill out missing dbx_path or local_path
                if exc.dbx_path or exc.local_path:
                    if not exc.local_path:
                        exc.local_path = self.to_local_path(exc.dbx_path)
                    if not exc.dbx_path:
                        exc.dbx_path = self.to_dbx_path(exc.local_path)

                if exc.dbx_path_dst or exc.local_path_dst:
                    if not exc.local_path_dst:
                        exc.local_path_dst = self.to_local_path(exc.dbx_path_dst)
                    if not exc.dbx_path:
                        exc.dbx_path_dst = self.to_dbx_path(exc.local_path_dst)

                if exc.dbx_path:
                    # we have a file / folder associated with the sync error
                    file_name = osp.basename(exc.dbx_path)
                    logger.warning('Could not sync %s', file_name, exc_info=True)
                    self.sync_errors.put(exc)

                    # save download errors to retry later
                    if download:
                        self.download_errors.add(exc.dbx_path)

                res = False

            return res

        return wrapper

    return decorator