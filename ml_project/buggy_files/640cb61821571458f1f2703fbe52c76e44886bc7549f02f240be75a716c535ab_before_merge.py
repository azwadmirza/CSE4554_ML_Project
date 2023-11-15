    def walk(self, top, topdown=True, ignore_file_handler=None):
        """Directory tree generator.

        See `os.walk` for the docs. Differences:
        - no support for symlinks
        - it could raise exceptions, there is no onerror argument
        """

        def onerror(e):
            raise e

        for root, dirs, files in dvc_walk(
            top,
            topdown=topdown,
            onerror=onerror,
            ignore_file_handler=ignore_file_handler,
        ):
            yield os.path.normpath(root), dirs, files