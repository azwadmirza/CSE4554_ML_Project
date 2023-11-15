    def configure_setting(self, name, prompt=None, default=NO_DEFAULT):
        """Return a validated value for this attribute from the terminal.

        ``prompt`` will be the docstring of the attribute if not given.

        If ``default`` is passed, it will be used if no value is given by the
        user. If it is not passed, the current value of the setting, or the
        default value if it's unset, will be used. Note that if ``default`` is
        passed, the current value of the setting will be ignored, even if it is
        not the attribute's default.
        """
        clazz = getattr(self.__class__, name)
        prompt = prompt or clazz.__doc__
        if default is NO_DEFAULT:
            try:
                default = getattr(self, name)
            except AttributeError:
                pass
            except ValueError:
                print('The configured value for this option was invalid.')
                if clazz.default is not NO_DEFAULT:
                    default = clazz.default
        while True:
            try:
                value = clazz.configure(prompt, default)
            except ValueError as exc:
                print(exc)
            else:
                break
        setattr(self, name, value)