    def _recursive_extract(data, path, seen_meta, level=0):
        if isinstance(data, dict):
            data = [data]
        if len(path) > 1:
            for obj in data:
                for val, key in zip(meta, meta_keys):
                    if level + 1 == len(val):
                        seen_meta[key] = _pull_field(obj, val[-1])

                _recursive_extract(obj[path[0]], path[1:],
                                   seen_meta, level=level + 1)
        else:
            for obj in data:
                recs = _pull_field(obj, path[0])

                # For repeating the metadata later
                lengths.append(len(recs))

                for val, key in zip(meta, meta_keys):
                    if level + 1 > len(val):
                        meta_val = seen_meta[key]
                    else:
                        try:
                            meta_val = _pull_field(obj, val[level:])
                        except KeyError as e:
                            if errors == 'ignore':
                                meta_val = np.nan
                            else:
                                raise KeyError("Try running with "
                                               "errors='ignore' as key "
                                               "{err} is not always present"
                                               .format(err=e))
                    meta_vals[key].append(meta_val)

                records.extend(recs)