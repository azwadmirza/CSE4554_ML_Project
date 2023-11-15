    def parse_tag_info(self, f):
        """ Parse HOMER tagdirectory taginfo.txt file to extract statistics in the first 11 lines. """
        # General Stats Table
        tag_info = dict()
        for l in f['f']:
            s = l.split("=")
            if len(s) > 1:
                if s[0].strip() == 'genome':
                    ss = s[1].split("\t")
                    if len(ss) > 2:
                        tag_info['genome'] = ss[0].strip()
                        try:
                            tag_info['UniqPositions'] = float(ss[1].strip())
                            tag_info['TotalPositions'] = float(ss[2].strip())
                        except:
                            tag_info['UniqPositions'] = ss[1].strip()
                            tag_info['TotalPositions'] = ss[2].strip()
                try:
                    tag_info[s[0].strip()] = float(s[1].strip())
                except ValueError:
                    tag_info[s[0].strip()] = s[1].strip()
        return tag_info