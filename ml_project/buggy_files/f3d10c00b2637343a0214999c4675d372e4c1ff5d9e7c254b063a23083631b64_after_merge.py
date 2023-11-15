    def _on_obex_owner_changed(self, owner):
        dprint("obex owner changed:", owner)
        if owner == "":
            self._unregister_agent()
        else:
            self._register_agent()