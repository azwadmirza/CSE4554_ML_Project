    def parse_tag_info_chrs(self, f, convChr=True):
        """ Parse HOMER tagdirectory taginfo.txt file to extract chromosome coverage. """
        parsed_data_total = OrderedDict()
        parsed_data_uniq = OrderedDict()
        remove = ["hap", "random", "chrUn", "cmd", "EBV", "GL", "NT_"]
        for l in f['f']:
            s = l.split("\t")
            key = s[0].strip()
            # skip header
            if '=' in l or len(s) != 3:
                continue
            if convChr:
                if any(x in key for x in remove):
                    continue
            try:
                vT = float(s[1].strip())
                vU = float(s[2].strip())
            except ValueError:
                continue

            parsed_data_total[key] = vT
            parsed_data_uniq[key] = vU

        return [parsed_data_total, parsed_data_uniq]