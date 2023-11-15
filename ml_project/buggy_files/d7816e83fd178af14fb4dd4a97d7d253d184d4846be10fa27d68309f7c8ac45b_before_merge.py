    def GET(self, key):
        page = web.ctx.site.get(key)
        if not page:
            raise web.notfound("")
        else:
            from infogami.utils import template
            import opds
            try:
                result = template.typetemplate('opds')(page, opds)
            except:
                raise web.notfound("")
            else:
                return delegate.RawText(result, content_type=" application/atom+xml;profile=opds")