    def __getitem__(self, key):
        """Get value for given key."""
        for altkey in self.form.scales.keys():
            try:
                try:
                    return (da.from_array(self.sections[altkey][key], chunks=CHUNK_SIZE)
                            * self.form.scales[altkey][key])
                except TypeError:
                    val = self.sections[altkey][key].decode().split("=")[1]
                    try:
                        return float(val) * self.form.scales[altkey][key]
                    except ValueError:
                        return val.strip()
            except (KeyError, ValueError):
                continue
        raise KeyError("No matching value for " + str(key))