    def _onActiveExtruderChanged(self):
        new_active_stack = ExtruderManager.getInstance().getActiveExtruderStack()
        if not new_active_stack:
            self._active_container_stack = None
            return

        if new_active_stack != self._active_container_stack:  # Check if changed
            if self._active_container_stack:  # Disconnect signal from old container (if any)
                self._active_container_stack.propertyChanged.disconnect(self._onPropertyChanged)
                self._active_container_stack.containersChanged.disconnect(self._onContainersChanged)

            self._active_container_stack = new_active_stack
            self._active_container_stack.propertyChanged.connect(self._onPropertyChanged)
            self._active_container_stack.containersChanged.connect(self._onContainersChanged)
            self._update()  # Ensure that the settings_with_inheritance_warning list is populated.