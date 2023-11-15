    def open_closed_files(self):
        """Open some closed files if they may have new lines.

        Opening more files may require us to close some of the already open
        files.
        """
        if not self.can_open_more_files:
            # If we can't open any more files. Close all of the files.
            self.close_all_files()

        files_with_no_updates = []
        while len(self.closed_file_infos) > 0:
            if (len(self.open_file_infos) >=
                    ray_constants.LOG_MONITOR_MAX_OPEN_FILES):
                self.can_open_more_files = False
                break

            file_info = self.closed_file_infos.pop(0)
            assert file_info.file_handle is None
            # Get the file size to see if it has gotten bigger since we last
            # opened it.
            try:
                file_size = os.path.getsize(file_info.filename)
            except (IOError, OSError) as e:
                # Catch "file not found" errors.
                if e.errno == errno.ENOENT:
                    logger.warning("Warning: The file {} was not "
                                   "found.".format(file_info.filename))
                    self.log_filenames.remove(file_info.filename)
                    continue
                raise e

            # If some new lines have been added to this file, try to reopen the
            # file.
            if file_size > file_info.size_when_last_opened:
                try:
                    f = open(file_info.filename, "r")
                except (IOError, OSError) as e:
                    if e.errno == errno.ENOENT:
                        logger.warning("Warning: The file {} was not "
                                       "found.".format(file_info.filename))
                        self.log_filenames.remove(file_info.filename)
                        continue
                    else:
                        raise e

                f.seek(file_info.file_position)
                file_info.filesize_when_last_opened = file_size
                file_info.file_handle = f
                self.open_file_infos.append(file_info)
            else:
                files_with_no_updates.append(file_info)

        # Add the files with no changes back to the list of closed files.
        self.closed_file_infos += files_with_no_updates