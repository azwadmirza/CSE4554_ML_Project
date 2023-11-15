    def _do_lock(self):
        try:
            with Tqdm(
                bar_format="{desc}",
                disable=not self._friendly,
                desc=(
                    "If DVC froze, see `hardlink_lock` in {}".format(
                        format_link("man.dvc.org/config#core")
                    )
                ),
            ):
                self._lock = zc.lockfile.LockFile(self.lockfile)
        except zc.lockfile.LockError:
            raise LockError(FAILED_TO_LOCK_MESSAGE)