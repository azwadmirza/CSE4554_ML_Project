    def dumpd(self):
        rel_wdir = os.path.relpath(self.wdir, os.path.dirname(self.path))
        return {
            key: value
            for key, value in {
                Stage.PARAM_MD5: self.md5,
                Stage.PARAM_CMD: self.cmd,
                Stage.PARAM_WDIR: pathlib.PurePath(rel_wdir).as_posix(),
                Stage.PARAM_LOCKED: self.locked,
                Stage.PARAM_DEPS: [d.dumpd() for d in self.deps],
                Stage.PARAM_OUTS: [o.dumpd() for o in self.outs],
                Stage.PARAM_META: self._state.get("meta"),
            }.items()
            if value
        }