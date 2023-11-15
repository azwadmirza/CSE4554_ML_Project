    def _check(self, reference, manifest, remote, path):
        if os.path.exists(path):
            existing_manifest = FileTreeManifest.loads(load(path))
            if existing_manifest.file_sums == manifest.file_sums:
                self._log.append("Manifest for '%s': OK" % str(reference))
                return

        if self._verify:
            raise ConanException("Modified or new manifest '%s' detected.\n"
                                 "Remote: %s\nProject manifest doesn't match installed one"
                                 % (str(reference), remote))

        self._handle_add(reference, remote, manifest, path)