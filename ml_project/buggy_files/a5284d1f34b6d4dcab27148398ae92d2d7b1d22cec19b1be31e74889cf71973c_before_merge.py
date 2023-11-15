    def decorate(overload_func):
        template = make_overload_method_template(typ, attr, overload_func)
        infer_getattr(template)
        return overload_func