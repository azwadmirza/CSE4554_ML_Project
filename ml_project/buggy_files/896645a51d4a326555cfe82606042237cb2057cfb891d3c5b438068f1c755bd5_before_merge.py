    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        color = None
        if self.ctx is not None:
            color = self.ctx.color
        if self.extra:
            if isinstance(self.extra, six.string_types):
                self.extra = [self.extra,]
            for extra in self.extra:
                if color:
                    extra = getattr(crayons, color, "blue")(extra)
                click_echo(fix_utf8(extra), file=file)
        hint = ''
        if (self.cmd is not None and
                self.cmd.get_help_option(self.ctx) is not None):
            hint = ('Try "%s %s" for help.\n'
                    % (self.ctx.command_path, self.ctx.help_option_names[0]))
        if self.ctx is not None:
            click_echo(self.ctx.get_usage() + '\n%s' % hint, file=file, color=color)
        click_echo(self.message, file=file)