    def generate_key(*args, **kw):
        show_key = namespace + '_' + text_type(args[1])
        if PY2:
            return show_key.encode('utf-8')
        return show_key