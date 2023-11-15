    def decorate(overload_func):
        template = make_overload_method_template(
            typ, attr, overload_func,
            inline=kwargs.get('inline', 'never'),
        )
        infer_getattr(template)
        overload(overload_func, **kwargs)(overload_func)
        return overload_func