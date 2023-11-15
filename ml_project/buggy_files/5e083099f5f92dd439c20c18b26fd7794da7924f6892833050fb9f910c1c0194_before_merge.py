    def fastqc_general_stats(self):
        """ Add some single-number stats to the basic statistics
        table at the top of the report """

        # Prep the data
        data = dict()
        for s_name in self.fastqc_data:
            bs = self.fastqc_data[s_name]['basic_statistics']
            data[s_name] = {
                'percent_gc': bs['%GC'],
                'avg_sequence_length': bs['avg_sequence_length'],
                'total_sequences': bs['Total Sequences'],
            }
            try:
                data[s_name]['percent_duplicates'] = 100 - bs['total_deduplicated_percentage']
            except KeyError:
                pass # Older versions of FastQC don't have this
            # Add count of fail statuses
            num_statuses = 0
            num_fails = 0
            for s in self.fastqc_data[s_name]['statuses'].values():
                num_statuses += 1
                if s == 'fail':
                    num_fails += 1
            data[s_name]['percent_fails'] = (float(num_fails)/float(num_statuses))*100.0

        # Are sequence lengths interesting?
        seq_lengths = [x['avg_sequence_length'] for x in data.values()]
        hide_seq_length = False if max(seq_lengths) - min(seq_lengths) > 10 else True

        headers = OrderedDict()
        headers['percent_duplicates'] = {
            'title': '% Dups',
            'description': '% Duplicate Reads',
            'max': 100,
            'min': 0,
            'suffix': '%',
            'scale': 'RdYlGn-rev'
        }
        headers['percent_gc'] = {
            'title': '% GC',
            'description': 'Average % GC Content',
            'max': 100,
            'min': 0,
            'suffix': '%',
            'scale': 'Set1',
            'format': '{:,.0f}'
        }
        headers['avg_sequence_length'] = {
            'title': 'Length',
            'description': 'Average Sequence Length (bp)',
            'min': 0,
            'suffix': ' bp',
            'scale': 'RdYlGn',
            'format': '{:,.0f}',
            'hidden': hide_seq_length
        }
        headers['percent_fails'] = {
            'title': '% Failed',
            'description': 'Percentage of modules failed in FastQC report (includes those not plotted here)',
            'max': 100,
            'min': 0,
            'suffix': '%',
            'scale': 'Reds',
            'format': '{:,.0f}',
            'hidden': True
        }
        headers['total_sequences'] = {
            'title': '{} Seqs'.format(config.read_count_prefix),
            'description': 'Total Sequences ({})'.format(config.read_count_desc),
            'min': 0,
            'scale': 'Blues',
            'modify': lambda x: x * config.read_count_multiplier,
            'shared_key': 'read_count'
        }
        self.general_stats_addcols(data, headers)