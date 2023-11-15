    def update_log_filenames(self):
        """Update the list of log files to monitor."""
        # output of user code is written here
        log_file_paths = glob.glob(f"{self.logs_dir}/worker*[.out|.err]")
        # segfaults and other serious errors are logged here
        raylet_err_paths = glob.glob(f"{self.logs_dir}/raylet*.err")
        # If gcs server restarts, there can be multiple log files.
        gcs_err_path = glob.glob(f"{self.logs_dir}/gcs_server*.err")
        for file_path in log_file_paths + raylet_err_paths + gcs_err_path:
            if os.path.isfile(
                    file_path) and file_path not in self.log_filenames:
                job_match = JOB_LOG_PATTERN.match(file_path)
                if job_match:
                    job_id = job_match.group(2)
                    worker_pid = job_match.group(3)
                else:
                    job_id = None
                    worker_pid = None

                is_err_file = file_path.endswith("err")

                self.log_filenames.add(file_path)
                self.closed_file_infos.append(
                    LogFileInfo(
                        filename=file_path,
                        size_when_last_opened=0,
                        file_position=0,
                        file_handle=None,
                        is_err_file=is_err_file,
                        job_id=job_id,
                        worker_pid=worker_pid))
                log_filename = os.path.basename(file_path)
                logger.info(f"Beginning to track file {log_filename}")