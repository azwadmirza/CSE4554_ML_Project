    def __repr__(self):
        init = self.__init__

        # This test looks for a single layer of wrapping performed by
        # functools.update_wrapper, commonly used in decorators. This will
        # allow RepresentationMixin to see through a single such decorator
        # applied to the __init__ method of a class, and find the underlying
        # arguments. It will not see through multiple layers of such
        # decorators, or cope with other decorators which do not use
        # functools.update_wrapper.

        if hasattr(init, '__wrapped__'):
            init = init.__wrapped__

        argspec = inspect.getfullargspec(init)
        if len(argspec.args) > 1 and argspec.defaults is not None:
            defaults = dict(zip(reversed(argspec.args), reversed(argspec.defaults)))
        else:
            defaults = {}

        for arg in argspec.args[1:]:
            if not hasattr(self, arg):
                template = 'class {} uses {} in the constructor, but does not define it as an attribute'
                raise AttributeError(template.format(self.__class__.__name__, arg))

        if len(defaults) != 0:
            args = [getattr(self, a) for a in argspec.args[1:-len(defaults)]]
        else:
            args = [getattr(self, a) for a in argspec.args[1:]]
        kwargs = {key: getattr(self, key) for key in defaults}

        def assemble_multiline(args, kwargs):
            def indent(text):
                lines = text.splitlines()
                if len(lines) <= 1:
                    return text
                return "\n".join("    " + l for l in lines).strip()
            args = ["\n    {},".format(indent(repr(a))) for a in args]
            kwargs = ["\n    {}={}".format(k, indent(repr(v)))
                      for k, v in sorted(kwargs.items())]

            info = "".join(args) + ", ".join(kwargs)
            return self.__class__.__name__ + "({}\n)".format(info)

        def assemble_line(args, kwargs):
            kwargs = ['{}={}'.format(k, repr(v)) for k, v in sorted(kwargs.items())]

            info = ", ".join([repr(a) for a in args] + kwargs)
            return self.__class__.__name__ + "({})".format(info)

        if len(assemble_line(args, kwargs)) <= self.__class__.__max_width__:
            return assemble_line(args, kwargs)
        else:
            return assemble_multiline(args, kwargs)