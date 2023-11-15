    def check_log_files_and_publish_updates(self):
        """Get any changes to the log files and push updates to Redis.

        Returns:
            True if anything was published and false otherwise.
        """
        anything_published = False
        for file_info in self.open_file_infos:
            assert not file_info.file_handle.closed

            lines_to_publish = []
            max_num_lines_to_read = 100
            for _ in range(max_num_lines_to_read):
                try:
                    next_line = file_info.file_handle.readline()
                    # Replace any characters not in UTF-8 with
                    # a replacement character, see
                    # https://stackoverflow.com/a/38565489/10891801
                    next_line = next_line.decode("utf-8", "replace")
                    if next_line == "":
                        break
                    if next_line[-1] == "\n":
                        next_line = next_line[:-1]
                    lines_to_publish.append(next_line)
                except Exception:
                    logger.error("Error: Reading file: {}, position: {} "
                                 "failed.".format(
                                     file_info.full_path,
                                     file_info.file_info.file_handle.tell()))
                    raise

            if file_info.file_position == 0:
                if (len(lines_to_publish) > 0 and
                        lines_to_publish[0].startswith("Ray worker pid: ")):
                    file_info.worker_pid = int(
                        lines_to_publish[0].split(" ")[-1])
                    lines_to_publish = lines_to_publish[1:]
                elif "/raylet" in file_info.filename:
                    file_info.worker_pid = "raylet"

            # Record the current position in the file.
            file_info.file_position = file_info.file_handle.tell()

            if len(lines_to_publish) > 0:
                self.redis_client.publish(
                    ray.gcs_utils.LOG_FILE_CHANNEL,
                    json.dumps({
                        "ip": self.ip,
                        "pid": file_info.worker_pid,
                        "lines": lines_to_publish
                    }))
                anything_published = True

        return anything_published