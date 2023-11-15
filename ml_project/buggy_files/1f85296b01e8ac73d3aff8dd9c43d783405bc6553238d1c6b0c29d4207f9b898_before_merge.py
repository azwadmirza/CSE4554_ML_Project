    def _paths_checksums():
        """
        A dictionary of checksums addressed by relpaths collected from
        the current tree outputs.

        To help distinguish between a directory and a file output,
        the former one will come with a trailing slash in the path:

            directory: "data/"
            file:      "data"
        """

        def _to_path(output):
            return (
                str(output)
                if not output.is_dir_checksum
                else os.path.join(str(output), "")
            )

        on_working_tree = isinstance(self.tree, LocalTree)

        def _to_checksum(output):
            if on_working_tree:
                return self.cache.local.tree.get_hash(output.path_info)[1]
            return output.checksum

        def _exists(output):
            if on_working_tree:
                return output.exists
            return True

        return {
            _to_path(output): _to_checksum(output)
            for stage in self.stages
            for output in stage.outs
            if _exists(output)
        }