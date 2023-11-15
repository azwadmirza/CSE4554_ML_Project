    def __call__(self, environ, start_response):
        environ['web'] = self.web
        return self.app(environ, start_response)