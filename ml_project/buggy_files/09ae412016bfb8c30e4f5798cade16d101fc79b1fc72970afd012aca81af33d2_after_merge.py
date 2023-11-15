    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        if self.extra:
            if isinstance(self.extra, six.string_types):
                self.extra = [self.extra,]
            for extra in self.extra:
                click_echo(decode_for_output(extra, file), file=file)
        click_echo(self.message, file=file)