    def __call__(self, element, compiler, **kw):
        # TODO: yes, this could also switch off of DBAPI in use.
        fn = self.specs.get(compiler.dialect.name, None)
        if not fn:
            try:
                fn = self.specs["default"]
            except KeyError as ke:
                util.raise_(
                    exc.UnsupportedCompilationError(
                        compiler,
                        type(element),
                        message="%s construct has no default "
                        "compilation handler." % type(element),
                    ),
                    replace_context=ke,
                )

        return fn(element, compiler, **kw)