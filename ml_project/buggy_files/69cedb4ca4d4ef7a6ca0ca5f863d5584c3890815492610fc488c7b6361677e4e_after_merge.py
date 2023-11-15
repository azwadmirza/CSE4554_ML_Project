    def get_file_hash(self, path_info):
        # NOTE: pyarrow doesn't support checksum, so we need to use hadoop
        regex = r".*\t.*\t(?P<checksum>.*)"
        stdout = self.hadoop_fs(
            f"checksum {path_info.url}", user=path_info.user
        )
        return HashInfo(
            self.PARAM_CHECKSUM, self._group(regex, stdout, "checksum")
        )