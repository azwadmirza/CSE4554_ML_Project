    def clear_old_remotes(self):
        '''
        Remove cache directories for remotes no longer configured
        '''
        try:
            cachedir_ls = os.listdir(self.cache_root)
        except OSError:
            cachedir_ls = []
        # Remove actively-used remotes from list
        for repo in self.remotes:
            try:
                cachedir_ls.remove(repo.cachedir_basename)
            except ValueError:
                pass
        to_remove = []
        for item in cachedir_ls:
            if item in ('gitfs', 'refs'):
                continue
            path = os.path.join(self.cache_root, item)
            if os.path.isdir(path):
                to_remove.append(path)
        failed = []
        if to_remove:
            for rdir in to_remove:
                try:
                    shutil.rmtree(rdir)
                except OSError as exc:
                    log.error(
                        'Unable to remove old {0} remote cachedir {1}: {2}'
                        .format(self.role, rdir, exc)
                    )
                    failed.append(rdir)
                else:
                    log.debug(
                        '{0} removed old cachedir {1}'.format(self.role, rdir)
                    )
        for fdir in failed:
            to_remove.remove(fdir)
        ret = bool(to_remove)
        if ret:
            self.write_remote_map()
        return ret