    def add_general_stats(self):
        data = {}
        for key in self.bcl2fastq_bysample.keys():
            try:
                perfectPercent = float( 100.0 * self.bcl2fastq_bysample[key]["perfectIndex"] / self.bcl2fastq_bysample[key]["total"] )
            except ZeroDivisionError:
                perfectPercent = 0
            data[key] = {
                "yieldQ30": self.bcl2fastq_bysample[key]["yieldQ30"],
                "total": self.bcl2fastq_bysample[key]["total"],
                "perfectPercent": '{0:.1f}'.format(perfectPercent),
                "trimmedPercent": self.bcl2fastq_bysample[key]['percent_trimmed']
            }
        headers = OrderedDict()
        headers['total'] = {
            'title': '{} Clusters'.format(config.read_count_prefix),
            'description': 'Total number of reads for this sample as determined by bcl2fastq demultiplexing ({})'.format(config.read_count_desc),
            'scale': 'Blues',
            'shared_key': 'read_count'
        }
        headers['yieldQ30'] = {
            'title': '{} Yield &ge; Q30'.format(config.base_count_prefix),
            'description': 'Number of bases with a Phred score of 30 or higher ({})'.format(config.base_count_desc),
            'scale': 'Greens',
            'shared_key': 'base_count'
        }
        headers['perfectPercent'] = {
            'title': '% Perfect Index',
            'description': 'Percent of reads with perfect index (0 mismatches)',
            'max': 100,
            'min': 0,
            'scale': 'RdYlGn',
            'suffix': '%'
        }
        headers['trimmedPercent'] = {
            'title': '% Bases trimmed',
            'description': 'Percent of bases trimmed',
            'max': 100,
            'min': 0,
            'scale': 'Reds',
            'suffix': '%',
            'hidden': True if all(data[s]['trimmedPercent'] == 0 for s in data) else False
        }
        self.general_stats_addcols(data, headers)