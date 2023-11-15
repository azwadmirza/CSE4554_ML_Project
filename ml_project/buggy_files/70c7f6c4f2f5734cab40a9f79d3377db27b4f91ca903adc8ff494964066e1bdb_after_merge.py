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

        # if compilation includes add_to_result_map, collect add_to_result_map
        # arguments from the user-defined callable, which are probably none
        # because this is not public API.  if it wasn't called, then call it
        # ourselves.
        arm = kw.get("add_to_result_map", None)
        if arm:
            arm_collection = []
            kw["add_to_result_map"] = lambda *args: arm_collection.append(args)

        expr = fn(element, compiler, **kw)

        if arm:
            if not arm_collection:
                arm_collection.append(
                    (None, None, (element,), sqltypes.NULLTYPE)
                )
            for tup in arm_collection:
                arm(*tup)
        return expr