    def _save(self):
        dname = os.path.dirname(self._path)
        with tempfile.NamedTemporaryFile(dir=dname, delete=False) as outf:
            # TODO replace with encoding='utf-8' and mode 'w+' in v8
            tname = outf.name
            data = json.dumps(self._local.data, sort_keys=True, indent=2)
            try:
                outf.write(data)
            except TypeError:
                outf.write(data.encode('utf-8'))
        shutil.move(tname, self._path)