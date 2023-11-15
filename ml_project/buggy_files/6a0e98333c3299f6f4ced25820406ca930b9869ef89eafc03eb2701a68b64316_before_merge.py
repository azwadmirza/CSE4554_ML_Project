    def options(self, request, *args, **kwargs):
        r = Response.text("ok")
        if self.ds.cors:
            r.headers["Access-Control-Allow-Origin"] = "*"
        return r