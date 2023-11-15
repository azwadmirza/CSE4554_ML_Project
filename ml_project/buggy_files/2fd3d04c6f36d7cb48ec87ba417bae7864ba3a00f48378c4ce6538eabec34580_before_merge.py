    def _on_adapter_property_changed(self, _adapter, key, value):
        if key == "Powered":
            if value and not self.CurrentState:
                dprint("adapter powered on while in off state, turning bluetooth on")
                self.RequestPowerState(True)

            self.UpdatePowerState()