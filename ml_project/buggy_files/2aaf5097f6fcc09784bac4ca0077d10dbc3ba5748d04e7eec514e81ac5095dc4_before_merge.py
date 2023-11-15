    def index(self, path='', includeFiles=False, *args, **kwargs):
        # @TODO: Move all cache control headers to the whole API end point so nothing's cached
        self.set_header('Cache-Control', 'max-age=0,no-cache,no-store')
        self.set_header('Content-Type', 'application/json')
        return json.dumps(list_folders(path, True, bool(int(includeFiles))))