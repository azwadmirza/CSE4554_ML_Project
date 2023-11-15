        def mkopt(name):
            return select.Option(
                i,
                None,
                lambda: self.master.options.console_palette == name,
                lambda: setattr(self.master.options, "palette", name)
            )