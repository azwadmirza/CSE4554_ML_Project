    def _MoveDownload(self, download_state, new_dir):
        def rename_or_merge(old, new):
            if os.path.exists(old):
                if os.path.exists(new):
                    files = os.listdir(old)
                    for file in files:
                        oldfile = os.path.join(old, file)
                        newfile = os.path.join(new, file)

                        if os.path.isdir(oldfile):
                            self.rename_or_merge(oldfile, newfile)

                        elif os.path.exists(newfile):
                            os.remove(newfile)
                            shutil.move(oldfile, newfile)
                        else:
                            shutil.move(oldfile, newfile)
                else:
                    os.renames(old, new)

        destdirs = download_state.get_download().get_dest_files()
        if len(destdirs) > 1:
            old = os.path.commonprefix([os.path.split(path)[0] for _, path in destdirs])
            _, old_dir = new = os.path.split(old)
            new = os.path.join(new_dir, old_dir)
        else:
            old = destdirs[0][1]
            _, old_file = os.path.split(old)
            new = os.path.join(new_dir, old_file)

        self._logger.info("Creating new downloadconfig")

        # Move torrents
        storage_moved = False

        download = download_state.get_download()
        self._logger.info("Moving from %s to %s newdir %s", old, new, new_dir)
        download.move_storage(new_dir)
        if download.get_save_path() == new_dir:
            storage_moved = True

        # If libtorrent hasn't moved the files yet, move them now
        if not storage_moved:
            self._logger.info("Moving from %s to %s newdir %s", old, new, new_dir)
            movelambda = lambda: rename_or_merge(old, new)
            self.guiutility.utility.session.lm.threadpool.add_task(movelambda, 0.0)