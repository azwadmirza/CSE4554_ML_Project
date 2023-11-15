    def save(self) -> None:
        """
        Create the writer & save.
        """
        # GH21227 internal compression is not used when file-like passed.
        if self.compression and hasattr(self.path_or_buf, "write"):
            warnings.warn(
                "compression has no effect when passing file-like object as input.",
                RuntimeWarning,
                stacklevel=2,
            )

        # when zip compression is called.
        is_zip = isinstance(self.path_or_buf, ZipFile) or (
            not hasattr(self.path_or_buf, "write") and self.compression == "zip"
        )

        if is_zip:
            # zipfile doesn't support writing string to archive. uses string
            # buffer to receive csv writing and dump into zip compression
            # file handle. GH21241, GH21118
            f = StringIO()
            close = False
        elif hasattr(self.path_or_buf, "write"):
            f = self.path_or_buf
            close = False
        else:
            f, handles = get_handle(
                self.path_or_buf,
                self.mode,
                encoding=self.encoding,
                compression=dict(self.compression_args, method=self.compression),
            )
            close = True

        try:
            # Note: self.encoding is irrelevant here
            self.writer = csvlib.writer(
                f,
                lineterminator=self.line_terminator,
                delimiter=self.sep,
                quoting=self.quoting,
                doublequote=self.doublequote,
                escapechar=self.escapechar,
                quotechar=self.quotechar,
            )

            self._save()

        finally:
            if is_zip:
                # GH17778 handles zip compression separately.
                buf = f.getvalue()
                if hasattr(self.path_or_buf, "write"):
                    self.path_or_buf.write(buf)
                else:
                    compression = dict(self.compression_args, method=self.compression)

                    f, handles = get_handle(
                        self.path_or_buf,
                        self.mode,
                        encoding=self.encoding,
                        compression=compression,
                    )
                    f.write(buf)
                    close = True
            if close:
                f.close()
                for _fh in handles:
                    _fh.close()
            elif self.should_close:
                f.close()