    def _summary_coord_extra(self, coord, indent):
        # Returns the text needed to ensure this coordinate can be
        # distinguished from all others with the same name.
        extra = ""
        similar_coords = self.coords(coord.name())
        if len(similar_coords) > 1:
            similar_coords.remove(coord)
            # Look for any attributes that vary.
            vary = set()
            for key, value in coord.attributes.items():
                for similar_coord in similar_coords:
                    if key not in similar_coord.attributes:
                        vary.add(key)
                        break
                    if not np.array_equal(
                        similar_coord.attributes[key], value
                    ):
                        vary.add(key)
                        break
            keys = sorted(vary)
            bits = [
                "{}={!r}".format(key, coord.attributes[key]) for key in keys
            ]
            if bits:
                extra = indent + ", ".join(bits)
        return extra