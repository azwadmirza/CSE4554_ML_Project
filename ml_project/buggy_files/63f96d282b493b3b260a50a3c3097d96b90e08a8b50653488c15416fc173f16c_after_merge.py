    def _execute(self, options, args):
        """Start the watcher."""
        try:
            from livereload import Server
        except ImportError:
            req_missing(['livereload>=2.0.0'], 'use the "auto" command')
            return

        # Run an initial build so we are uptodate
        subprocess.call(("nikola", "build"))

        port = options and options.get('port')

        server = Server()
        server.watch('conf.py')
        server.watch('themes/')
        server.watch('templates/')
        server.watch(self.site.config['GALLERY_PATH'])
        for item in self.site.config['post_pages']:
            server.watch(os.path.dirname(item[0]))
        for item in self.site.config['FILES_FOLDERS']:
            server.watch(os.path.dirname(item))

        out_folder = self.site.config['OUTPUT_FOLDER']
        if options and options.get('browser'):
            webbrowser.open('http://localhost:{0}'.format(port))

        server.serve(port, out_folder)