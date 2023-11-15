    def _local_inventory(self, cache):
        # for local files, perform BFS via os.scandir to determine existence of files
        # obtaining mtime and size of the files is deferred for parallel execution
        # as this can be a slow step on network filesystems
        path = self.inventory_root

        if not os.path.exists(path):
            cache.has_inventory.add(path)
            return

        start = time.time()

        logger.debug("Inventory started of {}".format(path))
        pbuffer = []
        counter = 0
        try:
            for entry in os.scandir(path):
                is_file = self._local_inventory_direntry_quick(cache, entry)

                if is_file is True:
                    counter += 1
                    pbuffer.append(entry.path)
                    if len(pbuffer) > 100:
                        cache.submit(self._local_inventory_path_complete, pbuffer)
                        pbuffer = []

            if pbuffer:
                cache.submit(self._local_inventory_path_complete, pbuffer)

            cache.has_inventory.add(path)
            logger.debug(
                "Inventory of {} completed in {:.1f} seconds. {} files added to stat queue ({} tasks in queue).".format(
                    path, time.time() - start, counter, cache.queue.qsize()
                )
            )

        except OSError as e:
            logger.debug(
                "Inventory of {} failed. Continuing without inventory caching. Error message: {}.".format(
                    path, str(e)
                )
            )