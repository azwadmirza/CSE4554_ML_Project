    def __call__(self, data, **metadata):
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        res = jsbeautifier.beautify(data, opts)
        return "JavaScript", format_text(res)