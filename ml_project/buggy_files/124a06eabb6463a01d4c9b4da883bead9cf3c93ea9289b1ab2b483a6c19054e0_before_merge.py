    def format_args(self, **kwargs: Any) -> str:
        if self.env.config.autodoc_typehints in ('none', 'description'):
            kwargs.setdefault('show_annotation', False)

        unwrapped = inspect.unwrap(self.object)
        try:
            if self.object == object.__init__ and self.parent != object:
                # Classes not having own __init__() method are shown as no arguments.
                #
                # Note: The signature of object.__init__() is (self, /, *args, **kwargs).
                #       But it makes users confused.
                args = '()'
            else:
                if inspect.isstaticmethod(unwrapped, cls=self.parent, name=self.object_name):
                    self.env.app.emit('autodoc-before-process-signature', unwrapped, False)
                    sig = inspect.signature(unwrapped, bound_method=False)
                else:
                    self.env.app.emit('autodoc-before-process-signature', unwrapped, True)
                    sig = inspect.signature(unwrapped, bound_method=True)
                args = stringify_signature(sig, **kwargs)
        except ValueError:
            args = ''

        if self.env.config.strip_signature_backslash:
            # escape backslashes for reST
            args = args.replace('\\', '\\\\')
        return args