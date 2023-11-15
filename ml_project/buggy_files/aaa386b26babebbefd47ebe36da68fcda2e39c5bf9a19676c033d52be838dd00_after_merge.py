    def __call__(self, environ, start_response):
        environ['web'] = self.web
        environ['stop_q'] = self.web.stop_q
        return self.app(environ, start_response)