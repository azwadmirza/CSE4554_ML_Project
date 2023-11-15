    def load_dir_cache(self, checksum):
        path_info = self.checksum_to_path_info(checksum)

        fobj = tempfile.NamedTemporaryFile(delete=False)
        path = fobj.name
        to_info = self.path_cls(path)
        self.cache.download([path_info], [to_info], no_progress_bar=True)

        try:
            with open(path, "r") as fobj:
                d = json.load(fobj)
        except ValueError:
            logger.exception("Failed to load dir cache '{}'".format(path_info))
            return []
        finally:
            os.unlink(path)

        if not isinstance(d, list):
            msg = "dir cache file format error '{}' [skipping the file]"
            logger.error(msg.format(relpath(path)))
            return []

        for info in d:
            # NOTE: here is a BUG, see comment to .as_posix() below
            relative_path = self.path_cls.from_posix(info[self.PARAM_RELPATH])
            info[self.PARAM_RELPATH] = relative_path.fspath

        return d