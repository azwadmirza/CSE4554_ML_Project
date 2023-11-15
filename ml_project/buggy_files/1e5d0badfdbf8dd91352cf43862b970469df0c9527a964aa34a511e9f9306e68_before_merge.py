    def _summary_coord_extra(self, coord, indent):
        # Returns the text needed to ensure this coordinate can be
        # distinguished from all others with the same name.
        extra = ""
        similar_coords = self.coords(coord.name())
        if len(similar_coords) > 1:
            # Find all the attribute keys
            keys = set()
            for similar_coord in similar_coords:
                keys.update(similar_coord.attributes.keys())
            # Look for any attributes that vary
            vary = set()
            attributes = {}
            for key in keys:
                for similar_coord in similar_coords:
                    if key not in similar_coord.attributes:
                        vary.add(key)
                        break
                    value = similar_coord.attributes[key]
                    if attributes.setdefault(key, value) != value:
                        vary.add(key)
                        break
            keys = sorted(vary & set(coord.attributes.keys()))
            bits = [
                "{}={!r}".format(key, coord.attributes[key]) for key in keys
            ]
            if bits:
                extra = indent + ", ".join(bits)
        return extra