    def keypress(self, size, key):
        if self.walker.editing:
            if key == "enter":
                foc, idx = self.get_focus()
                v = self.walker.get_edit_text()
                try:
                    d = self.master.options.parse_setval(foc.opt.name, v)
                    self.master.options.update(**{foc.opt.name: d})
                except exceptions.OptionsError as v:
                    signals.status_message.send(message=str(v))
                self.walker.stop_editing()
                return None
            elif key == "esc":
                self.walker.stop_editing()
                return None
        else:
            if key == "m_start":
                self.set_focus(0)
                self.walker._modified()
            elif key == "m_end":
                self.set_focus(len(self.walker.opts) - 1)
                self.walker._modified()
            elif key == "m_select":
                foc, idx = self.get_focus()
                if foc.opt.typespec == bool:
                    self.master.options.toggler(foc.opt.name)()
                    # Bust the focus widget cache
                    self.set_focus(self.walker.index)
                elif can_edit_inplace(foc.opt):
                    self.walker.start_editing()
                    self.walker._modified()
                elif foc.opt.choices:
                    self.master.overlay(
                        overlay.Chooser(
                            self.master,
                            foc.opt.name,
                            foc.opt.choices,
                            foc.opt.current(),
                            self.master.options.setter(foc.opt.name)
                        )
                    )
                elif foc.opt.typespec == Sequence[str]:
                    self.master.overlay(
                        overlay.OptionsOverlay(
                            self.master,
                            foc.opt.name,
                            foc.opt.current(),
                            HELP_HEIGHT + 5
                        ),
                        valign="top"
                    )
                else:
                    raise NotImplementedError()
        return super().keypress(size, key)