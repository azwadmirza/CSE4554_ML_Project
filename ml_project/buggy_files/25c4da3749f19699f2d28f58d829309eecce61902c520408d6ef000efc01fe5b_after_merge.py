    def parse_htseq_report (self, f):
        """ Parse the HTSeq Count log file. """
        keys = [ '__no_feature', '__ambiguous', '__too_low_aQual', '__not_aligned', '__alignment_not_unique' ]
        parsed_data = dict()
        assigned_counts = 0
        for l in f['f']:
            s = l.split("\t")
            if s[0] in keys:
                parsed_data[s[0][2:]] = int(s[1])
            else:
                try:
                    assigned_counts += int(s[1])
                except (ValueError, IndexError):
                    pass
        if len(parsed_data) > 0:
            parsed_data['assigned'] = assigned_counts
            parsed_data['total_count'] = sum([v for v in parsed_data.values()])
            parsed_data['percent_assigned'] = (float(parsed_data['assigned']) / float(parsed_data['total_count'])) * 100.0
            return parsed_data
        return None