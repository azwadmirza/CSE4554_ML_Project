    def _maybe_dedup_names(self, names):
        # see gh-7160 and gh-9424: this helps to provide
        # immediate alleviation of the duplicate names
        # issue and appears to be satisfactory to users,
        # but ultimately, not needing to butcher the names
        # would be nice!
        if self.mangle_dupe_cols:
            names = list(names)  # so we can index
            counts = defaultdict(int)
            is_potential_mi = _is_potential_multi_index(names)

            for i, col in enumerate(names):
                cur_count = counts[col]

                while cur_count > 0:
                    counts[col] = cur_count + 1

                    if is_potential_mi:
                        col = col[:-1] + (f"{col[-1]}.{cur_count}",)
                    else:
                        col = f"{col}.{cur_count}"
                    cur_count = counts[col]

                names[i] = col
                counts[col] = cur_count + 1

        return names