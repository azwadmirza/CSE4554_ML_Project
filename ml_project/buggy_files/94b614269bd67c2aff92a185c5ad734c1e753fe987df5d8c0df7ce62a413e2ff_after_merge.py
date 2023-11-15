    def _add_editcontrol(self, x, y, height, width):

        control = xbmcgui.ControlEdit(0, 0, 0, 0,
                                      label="",
                                      font="font13",
                                      textColor="FF00A4DC",
                                      disabledColor="FF888888",
                                      focusTexture="-",
                                      noFocusTexture="-")
        control.setPosition(x, y)
        control.setHeight(height)
        control.setWidth(width)

        self.addControl(control)
        return control