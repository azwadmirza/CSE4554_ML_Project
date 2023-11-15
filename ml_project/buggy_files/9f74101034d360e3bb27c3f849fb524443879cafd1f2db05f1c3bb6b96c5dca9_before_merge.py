    def face_color(self, face_color):
        # if the provided face color is a string, first check if it is a key in the properties.
        # otherwise, assume it is the name of a color
        if self._is_color_mapped(face_color):
            if guess_continuous(self.properties[face_color]):
                self._face_color_mode = ColorMode.COLORMAP
            else:
                self._face_color_mode = ColorMode.CYCLE
            self._face_color_property = face_color
            self.refresh_colors()

        else:
            transformed_color = transform_color_with_defaults(
                num_entries=len(self.data),
                colors=face_color,
                elem_name="face_color",
                default="white",
            )
            self._face_color = normalize_and_broadcast_colors(
                len(self.data), transformed_color
            )
            self.face_color_mode = ColorMode.DIRECT

            self.events.face_color()
            self.events.highlight()