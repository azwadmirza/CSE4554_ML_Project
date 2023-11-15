    def parse_tag_info_chrs(self, f, convChr=True):
        """ Parse HOMER tagdirectory taginfo.txt file to extract chromosome coverage. """
        parsed_data_total = dict()
        parsed_data_uniq = dict()
        remove = ["hap", "random", "chrUn", "cmd", "EBV", "GL", "NT_"]
        ## skip first 11 lines
        counter = 0
        for l in f['f']:
            ## skip first 11 lines
            if counter < 11:
                counter = counter + 1
                continue
            s = l.split("\t")

            key = s[0].strip()

            if len(s) > 1:
                if convChr:
                    if any(x in key for x in remove):
                        continue

                vT = float(s[1].strip())
                vU = float(s[2].strip())

                parsed_data_total[key] = vT
                parsed_data_uniq[key] = vU

        return [parsed_data_total, parsed_data_uniq]