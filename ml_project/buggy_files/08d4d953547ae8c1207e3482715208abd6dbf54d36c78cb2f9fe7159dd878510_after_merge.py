    def _onGCodePrefixMessage(self, message: Arcus.PythonMessage) -> None:
        try:
            self._scene.gcode_dict[self._start_slice_job_build_plate].insert(0, message.data.decode("utf-8", "replace")) #type: ignore #Because we generate this attribute dynamically.
        except KeyError:  # Can occur if the g-code has been cleared while a slice message is still arriving from the other end.
            pass  # Throw the message away.