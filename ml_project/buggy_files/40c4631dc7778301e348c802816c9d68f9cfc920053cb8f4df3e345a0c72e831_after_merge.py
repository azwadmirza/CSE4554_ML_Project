    def iocache(raise_error=False):
        def inner_iocache(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                iocache = self.rule.workflow.iocache
                if not iocache.active or self.inventory_path is None:
                    return func(self, *args, **kwargs)

                cache = getattr(iocache, func.__name__)
                # first check if file is present in cache
                if self.inventory_path in cache:
                    res = cache[self.inventory_path]
                # check if the folder was cached
                elif iocache.in_inventory(self.inventory_root):
                    # as the folder was cached, we do know that the file does not exist
                    if raise_error:
                        # make sure that the cache behaves the same as non-cached results
                        raise FileNotFoundError(
                            "No such file or directory: {}".format(self.file)
                        )
                    else:
                        return False
                elif self._is_function:
                    raise ValueError(
                        "This IOFile is specified as a function and "
                        "may not be used directly."
                    )
                else:
                    res = IOCACHE_DEFERRED

                if res is IOCACHE_DEFERRED:
                    # determine values that are not yet cached
                    self._add_to_inventory(func.__name__)
                    res = cache[self.inventory_path]

                # makes sure that cache behaves same as non-cached results
                if res is IOCACHE_BROKENSYMLINK:
                    raise WorkflowError(
                        "File {} seems to be a broken symlink.".format(self.file)
                    )
                elif res is IOCACHE_NOTEXIST:
                    raise FileNotFoundError("File {} does not exist.".format(self.file))
                elif res is IOCACHE_NOPERMISSION:
                    raise PermissionError(
                        "File {} does not have the required permissions.".format(
                            self.file
                        )
                    )
                return res

            return wrapper

        return inner_iocache