    def parse_tag_info(self, f):
        """ Parse HOMER tagdirectory taginfo.txt file to extract statistics in the first 11 lines. """
        # General Stats Table
        tag_info = dict()
        counter = 0
        for l in f['f']:
            if counter == 1:
                s = l.split("\t")
                tag_info['UniqPositions'] = float(s[1].strip())
                tag_info['TotalPositions'] = float(s[2].strip())
            if counter == 4:
                s = l.split("\t")
                tag_info['fragmentLengthEstimate'] = float(s[0].strip().split("=")[1])
            if counter == 5:
                s = l.split("\t")
                tag_info['peakSizeEstimate'] = float(s[0].strip().split("=")[1])
            if counter == 6:
                s = l.split("\t")
                tag_info['tagsPerBP'] = float(s[0].strip().split("=")[1])
            if counter == 7:
                s = l.split("\t")
                tag_info['averageTagsPerPosition'] = float(s[0].strip().split("=")[1])
            if counter == 8:
                s = l.split("\t")
                tag_info['averageTagLength'] = float(s[0].strip().split("=")[1])
            if counter == 9:
                s = l.split("\t")
                tag_info['gsizeEstimate'] = float(s[0].strip().split("=")[1])
            if counter == 10:
                s = l.split("\t")
                tag_info['averageFragmentGCcontent'] = float(s[0].strip().split("=")[1])
            if counter == 11:
                break
            counter = counter + 1
        return tag_info