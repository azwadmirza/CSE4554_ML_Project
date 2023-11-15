    def save_preferences(self, event):
        event.Skip()
        p = self.get_preferences()
        for control, (text, getter, setter, ui_info, help_text) in \
            zip(self.controls, p):
            if ui_info == COLOR:
                setter(control.BackgroundColour)
            elif ui_info == FILEBROWSE and os.path.isfile(control.Value):
                setter(control.Value)
            else:
                setter(control.Value)