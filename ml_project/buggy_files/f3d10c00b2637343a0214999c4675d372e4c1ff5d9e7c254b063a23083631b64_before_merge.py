    def _on_obex_owner_changed(self, owner):
        dprint("obex owner changed:", owner)
        if owner == "":
            self._agent = None
        else:
            self._agent = _Agent(self._applet)