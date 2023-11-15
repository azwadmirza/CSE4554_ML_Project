    def close_all_files(self):
        """Close all open files (so that we can open more)."""
        while len(self.open_file_infos) > 0:
            file_info = self.open_file_infos.pop(0)
            file_info.file_handle.close()
            file_info.file_handle = None
            try:
                # Test if the worker process that generated the log file
                # is still alive. Only applies to worker processes.
                if (file_info.worker_pid != "raylet"
                        and file_info.worker_pid != "gcs_server"
                        and file_info.worker_pid != "autoscaler"):
                    os.kill(file_info.worker_pid, 0)
            except OSError:
                # The process is not alive any more, so move the log file
                # out of the log directory so glob.glob will not be slowed
                # by it.
                target = os.path.join(self.logs_dir, "old",
                                      os.path.basename(file_info.filename))
                try:
                    shutil.move(file_info.filename, target)
                except (IOError, OSError) as e:
                    if e.errno == errno.ENOENT:
                        logger.warning(
                            f"Warning: The file {file_info.filename} "
                            "was not found.")
                    else:
                        raise e
            else:
                self.closed_file_infos.append(file_info)
        self.can_open_more_files = True