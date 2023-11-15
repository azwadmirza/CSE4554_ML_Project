    def complete(self, term, includeFiles=0, *args, **kwargs):
        self.set_header('Cache-Control', 'max-age=0,no-cache,no-store')
        self.set_header('Content-Type', 'application/json')
        paths = [entry['path'] for entry in list_folders(os.path.dirname(term), include_files=bool(int(includeFiles)))
                 if 'path' in entry]

        return json.dumps(paths)