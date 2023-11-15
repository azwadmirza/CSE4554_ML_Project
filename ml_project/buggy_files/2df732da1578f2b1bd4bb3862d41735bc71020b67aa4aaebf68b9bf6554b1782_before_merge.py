    def serve_static(self, environ, start_response):
        """Trivial static file server."""
        uri = wsgiref.util.request_uri(environ)
        p_uri = urlparse(uri)
        f_path = os.path.join(self.site.config['OUTPUT_FOLDER'], *p_uri.path.split('/'))
        mimetype = mimetypes.guess_type(uri)[0] or 'text/html'

        if os.path.isdir(f_path):
            f_path = os.path.join(f_path, self.site.config['INDEX_FILE'])

        if p_uri.path == '/robots.txt':
            start_response('200 OK', [('Content-type', 'text/plain')])
            return '''User-Agent: *\nDisallow: /\n'''
        elif os.path.isfile(f_path):
            with open(f_path, 'rb') as fd:
                start_response('200 OK', [('Content-type', mimetype)])
                return self.inject_js(mimetype, fd.read())
        elif p_uri.path == '/livereload.js':
            with open(LRJS_PATH) as fd:
                start_response('200 OK', [('Content-type', mimetype)])
                return self.inject_js(mimetype, fd.read())
        start_response('404 ERR', [])
        return self.inject_js('text/html', ERROR_N.format(404).format(uri))