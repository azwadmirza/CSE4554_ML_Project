    def _add_editcontrol(self, x, y, height, width, password=False):

        kwargs = dict(
            label="User",
            font="font13",
            textColor="FF00A4DC",
            disabledColor="FF888888",
            focusTexture="-",
            noFocusTexture="-"
        )

        # TODO: Kodi 17 compat removal cleanup
        if kodi_version() < 18:
            kwargs['isPassword'] = password

        control = xbmcgui.ControlEdit(0, 0, 0, 0, **kwargs)

        control.setPosition(x, y)
        control.setHeight(height)
        control.setWidth(width)

        self.addControl(control)

        # setType has no effect before the control is added to a window
        # TODO: Kodi 17 compat removal cleanup
        if password and not kodi_version() < 18:
            control.setType(xbmcgui.INPUT_TYPE_PASSWORD, "Please enter password")

        return control