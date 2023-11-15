    def _save(self):
        dname = os.path.dirname(self._path)
        with tempfile.NamedTemporaryFile(dir=dname, delete=False) as outf:
            tname = outf.name
            json.dump(self._local.data, outf, sort_keys=True, indent=2)
        shutil.move(tname, self._path)