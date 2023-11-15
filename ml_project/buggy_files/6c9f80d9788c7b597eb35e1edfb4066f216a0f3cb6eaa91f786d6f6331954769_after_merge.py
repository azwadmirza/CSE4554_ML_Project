    def update_from_options(self, frames: List[Frame]) -> bool:
        """Update the frame to reflect that each key will be updated
        as in one of the frames.  Return whether any item changes.

        If a key is declared as AnyType, only update it if all the
        options are the same.
        """

        frames = [f for f in frames if not f.unreachable]
        changed = False
        keys = set(key for f in frames for key in f)

        for key in keys:
            current_value = self._get(key)
            resulting_values = [f.get(key, current_value) for f in frames]
            if any(x is None for x in resulting_values):
                # We didn't know anything about key before
                # (current_value must be None), and we still don't
                # know anything about key in at least one possible frame.
                continue

            if isinstance(self.declarations.get(key), AnyType):
                type = resulting_values[0]
                if not all(is_same_type(type, t) for t in resulting_values[1:]):
                    type = AnyType()
            else:
                type = resulting_values[0]
                for other in resulting_values[1:]:
                    type = join_simple(self.declarations[key], type, other)
            if not is_same_type(type, current_value):
                self._push(key, type)
                changed = True

        self.frames[-1].unreachable = not frames

        return changed