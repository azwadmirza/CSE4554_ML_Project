    def parse_peddy_csv(self, f, pattern):
        """ Parse csv output from peddy """
        parsed_data = dict()
        headers = None
        s_name_idx = None
        for l in f['f'].splitlines():
            s = l.split(",")
            if headers is None:
                headers = s
                try:
                    s_name_idx = [headers.index("sample_id")]
                except ValueError:
                    try:
                        s_name_idx = [headers.index("sample_a"), headers.index("sample_b")]
                    except ValueError:
                        log.warn("Could not find sample name in Peddy output: {}".format(f['fn']))
                        return None
            else:
                s_name = '-'.join([s[idx] for idx in s_name_idx])
                parsed_data[s_name] = dict()
                for i, v in enumerate(s):
                    if i not in s_name_idx:
                        if headers[i] == "error" and pattern == "sex_check":
                            v = "True" if v == "False" else "False"
                        try:
                            # add the pattern as a suffix to key
                            parsed_data[s_name][headers[i] + "_" + pattern] = float(v)
                        except ValueError:
                            # add the pattern as a suffix to key
                            parsed_data[s_name][headers[i] + "_" + pattern] = v
        if len(parsed_data) == 0:
            return None
        return parsed_data