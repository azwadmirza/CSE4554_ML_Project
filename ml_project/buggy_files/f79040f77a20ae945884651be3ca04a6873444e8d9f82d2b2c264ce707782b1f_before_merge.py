    def set_selected_files(self, selected_files=None):
        if not isinstance(self.tdef, TorrentDefNoMetainfo):

            if selected_files is None:
                selected_files = self.get_selected_files()
            else:
                DownloadConfigInterface.set_selected_files(self, selected_files)

            is_multifile = len(self.orig_files) > 1
            commonprefix = os.path.commonprefix(self.orig_files) if is_multifile else u''
            swarmname = commonprefix.partition(os.path.sep)[0]
            unwanteddir = os.path.join(swarmname, u'.unwanted')
            unwanteddir_abs = os.path.join(self.get_save_path().decode('utf-8'), unwanteddir)

            filepriorities = []
            torrent_storage = get_info_from_handle(self.handle).files()

            for index, orig_path in enumerate(self.orig_files):
                filename = orig_path[len(swarmname) + 1:] if swarmname else orig_path

                if filename in selected_files or not selected_files:
                    filepriorities.append(1)
                    new_path = orig_path
                else:
                    filepriorities.append(0)
                    new_path = os.path.join(unwanteddir, '%s%d' % (hexlify(self.tdef.get_infohash()), index))

                # as from libtorrent 1.0, files returning file_storage (lazy-iterable)
                if hasattr(lt, 'file_storage') and isinstance(torrent_storage, lt.file_storage):
                    cur_path = torrent_storage.at(index).path.decode('utf-8')
                else:
                    cur_path = torrent_storage[index].path.decode('utf-8')

                if cur_path != new_path:
                    if not os.path.exists(unwanteddir_abs) and unwanteddir in new_path:
                        try:
                            os.makedirs(unwanteddir_abs)
                            if sys.platform == "win32":
                                ctypes.windll.kernel32.SetFileAttributesW(
                                    unwanteddir_abs, 2)  # 2 = FILE_ATTRIBUTE_HIDDEN
                        except OSError:
                            self._logger.error("LibtorrentDownloadImpl: could not create %s" % unwanteddir_abs)
                            # Note: If the destination directory can't be accessed, libtorrent will not be able to store the files.
                            # This will result in a DLSTATUS_STOPPED_ON_ERROR.

                    # Path should be unicode if Libtorrent is using std::wstring (on Windows),
                    # else we use str (on Linux).
                    try:
                        self.handle.rename_file(index, new_path)
                    except TypeError:
                        self.handle.rename_file(index, new_path.encode("utf-8"))

            # if in share mode, don't change priority of the file
            if not self.get_share_mode():
                self.handle.prioritize_files(filepriorities)

            self.unwanteddir_abs = unwanteddir_abs