    def symlink(
        self,
        src,  # type: str
        dst,  # type: str
        label=None,  # type: Optional[str]
    ):
        # type: (...) -> None
        dst = self._normalize(dst)
        self._tag(dst, label)
        self._ensure_parent(dst)
        abs_src = os.path.abspath(src)
        abs_dst = os.path.join(self.chroot, dst)
        os.symlink(abs_src, abs_dst)