    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        if self.extra:
            if isinstance(self.extra, six.string_types):
                self.extra = [self.extra,]
            for extra in self.extra:
                extra = "[pipenv.exceptions.{0!s}]: {1}".format(
                    self.__class__.__name__, extra
                )
                click_echo(extra, file=file)
        click_echo(fix_utf8("{0}".format(self.message)), file=file)