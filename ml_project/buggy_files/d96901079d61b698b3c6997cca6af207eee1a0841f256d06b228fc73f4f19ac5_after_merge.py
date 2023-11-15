    def _collect_dir(self, path_info):
        dir_info = []

        for root, dirs, files in self.walk(path_info):
            if len(files) > LARGE_DIR_SIZE:
                msg = (
                    "Computing md5 for a large directory {}. "
                    "This is only done once."
                )
                title = str(self.path_cls(root))
                logger.info(msg.format(title))
                files = progress(files, name=title)

            for fname in files:
                file_info = self.path_cls(root) / fname
                relative_path = file_info.relative_to(path_info)
                dir_info.append(
                    {
                        # NOTE: this is lossy transformation:
                        #   "hey\there" -> "hey/there"
                        #   "hey/there" -> "hey/there"
                        # The latter is fine filename on Windows,
                        # which will transform to dir/file on back transform.
                        #
                        # Yes, this is a BUG, as long as we permit "/" in
                        # filenames on Windows and "\" on Unix
                        self.PARAM_RELPATH: relative_path.as_posix(),
                        self.PARAM_CHECKSUM: self.get_file_checksum(file_info),
                    }
                )

        # NOTE: sorting the list by path to ensure reproducibility
        return sorted(dir_info, key=itemgetter(self.PARAM_RELPATH))