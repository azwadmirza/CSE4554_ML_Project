    def complete(self, term, includeFiles=False, *args, **kwargs):
        self.set_header('Cache-Control', 'max-age=0,no-cache,no-store')
        self.set_header('Content-Type', 'application/json')
        paths = [entry['path'] for entry in
                 list_folders(os.path.dirname(term), include_files=truth_to_bool(includeFiles))
                 if 'path' in entry]

        return json.dumps(paths)