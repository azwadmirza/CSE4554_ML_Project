    def _execute(self, options, args):
        """Start the watcher."""
        try:
            from livereload.server import start
        except ImportError:
            req_missing(['livereload==1.0.1'], 'use the "auto" command')
            return

        # Run an initial build so we are uptodate
        subprocess.call(("nikola", "build"))

        port = options and options.get('port')

        # Create a Guardfile
        with codecs.open("Guardfile", "wb+", "utf8") as guardfile:
            l = ["conf.py", "themes", "templates", self.site.config['GALLERY_PATH']]
            for item in self.site.config['post_pages']:
                l.append(os.path.dirname(item[0]))
            for item in self.site.config['FILES_FOLDERS']:
                l.append(os.path.dirname(item))
            data = GUARDFILE.format(json.dumps(l))
            guardfile.write(data)

        out_folder = self.site.config['OUTPUT_FOLDER']

        os.chmod("Guardfile", 0o755)

        start(port, out_folder, options and options.get('browser'))