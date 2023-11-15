    def _local_inventory(self, cache):
        # for local files, perform BFS via os.scandir to determine existence of files
        if cache.remaining_wait_time <= 0:
            # No more time to create inventory.
            return

        start_time = time.time()

        root = cache.get_inventory_root(self)
        if root == self:
            # there is no root directory that could be used
            return
        if os.path.exists(root):
            queue = [root]
            while queue:
                path = queue.pop(0)
                # path must be a dir
                cache.exists_local[path] = True
                with os.scandir(path) as scan:
                    for entry in scan:
                        if entry.is_dir():
                            queue.append(entry.path)
                        else:
                            # path is a file
                            cache.exists_local[entry.path] = True
                cache.remaining_wait_time -= time.time() - start_time
                if cache.remaining_wait_time <= 0:
                    # Stop, do not mark inventory as done below.
                    # Otherwise, we would falsely assume that those files
                    # are not present.
                    return

        cache.has_inventory.add(root)