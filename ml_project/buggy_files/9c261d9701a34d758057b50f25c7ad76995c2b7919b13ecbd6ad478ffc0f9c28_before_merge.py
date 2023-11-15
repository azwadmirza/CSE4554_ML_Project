    def detype(self):
        """De-types the instance, allowing it to be exported to the environment."""
        style = self.style
        if self._detyped is None:
            self._detyped = ":".join(
                [
                    key
                    + "="
                    + ";".join(
                        [
                            "target"
                            if v == "TARGET"
                            else ansi_color_name_to_escape_code(v, cmap=style)
                            for v in val
                        ]
                    )
                    for key, val in sorted(self._d.items())
                ]
            )
        return self._detyped