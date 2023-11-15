    def __str__(self):
        """
        Set the string representation of the class.
        """
        if self.filename:
            filename = self.filename
        else:
            filename = 'Unknown'
        if self.endian == '<':
            endian = 'Little Endian'
        else:
            endian = 'Big Endian'
        if self.did_goto:
            goto_info = (" (records were skipped, number is wrong in case "
                         "of differing record sizes)")
        else:
            goto_info = ""
        ret_val = ('FILE: %s\nRecord Number: %i%s\n' +
                   'Record Offset: %i byte\n' +
                   'Header Endianness: %s\n\n') % \
                  (filename, self.record_number, goto_info, self.record_offset,
                   endian)
        ret_val += 'FIXED SECTION OF DATA HEADER\n'
        for key in self.fixed_header.keys():
            ret_val += '\t%s: %s\n' % (key, self.fixed_header[key])
        ret_val += '\nBLOCKETTES\n'
        for key in self.blockettes.keys():
            ret_val += '\t%i:' % key
            if not len(self.blockettes[key]):
                ret_val += '\tNOT YET IMPLEMENTED\n'
            for _i, blkt_key in enumerate(self.blockettes[key].keys()):
                if _i == 0:
                    tabs = '\t'
                else:
                    tabs = '\t\t'
                ret_val += '%s%s: %s\n' % (tabs, blkt_key,
                                           self.blockettes[key][blkt_key])
        ret_val += '\nCALCULATED VALUES\n'
        ret_val += '\tCorrected Starttime: %s\n' % self.corrected_starttime
        return ret_val