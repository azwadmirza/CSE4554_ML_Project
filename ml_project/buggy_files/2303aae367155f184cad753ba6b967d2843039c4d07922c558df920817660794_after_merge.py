    def _filtered(self, paths: List[Path]):
        for p in paths:
            if p.suffix in self._all_music_ext:
                yield p