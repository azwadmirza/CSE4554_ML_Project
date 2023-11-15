        def _to_checksum(output):
            if on_working_tree:
                return self.cache.local.tree.get_hash(output.path_info).value
            return output.checksum