    def get_lockfile_meta(self):
        from .vendor.plette.lockfiles import PIPFILE_SPEC_CURRENT
        if self.lockfile_exists:
            sources = self.lockfile_content.get("_meta", {}).get("sources", [])
        else:
            sources = [dict(source) for source in self.parsed_pipfile["source"]]
        if not isinstance(sources, list):
            sources = [sources,]
        return {
            "hash": {"sha256": self.calculate_pipfile_hash()},
            "pipfile-spec": PIPFILE_SPEC_CURRENT,
            "sources": sources,
            "requires": self.parsed_pipfile.get("requires", {})
        }