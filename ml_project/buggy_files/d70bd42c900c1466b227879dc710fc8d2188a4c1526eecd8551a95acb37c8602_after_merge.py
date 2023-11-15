    def gc_content_plot (self):
        """ Create the HTML for the FastQC GC content plot """

        data = dict()
        data_norm = dict()
        for s_name in self.fastqc_data:
            try:
                data[s_name] = {d['gc_content']: d['count'] for d in self.fastqc_data[s_name]['per_sequence_gc_content']}
            except KeyError:
                pass
            else:
                data_norm[s_name] = dict()
                total = sum( [ c for c in data[s_name].values() ] )
                for gc, count in data[s_name].items():
                    try:
                        data_norm[s_name][gc] = (count / total) * 100
                    except ZeroDivisionError:
                        data_norm[s_name][gc] = 0
        if len(data) == 0:
            log.debug('per_sequence_gc_content not found in FastQC reports')
            return None

        pconfig = {
            'id': 'fastqc_per_sequence_gc_content_plot',
            'title': 'FastQC: Per Sequence GC Content',
            'xlab': '% GC',
            'ylab': 'Percentage',
            'ymin': 0,
            'xmax': 100,
            'xmin': 0,
            'yDecimals': False,
            'tt_label': '<b>{point.x}% GC</b>: {point.y}',
            'colors': self.get_status_cols('per_sequence_gc_content'),
            'data_labels': [
                {'name': 'Percentages', 'ylab': 'Percentage'},
                {'name': 'Counts', 'ylab': 'Count'}
            ]
        }

        # Try to find and plot a theoretical GC line
        theoretical_gc = None
        theoretical_gc_raw = None
        theoretical_gc_name = None
        for f in self.find_log_files('fastqc/theoretical_gc'):
            if theoretical_gc_raw is not None:
                log.warning("Multiple FastQC Theoretical GC Content files found, now using {}".format(f['fn']))
            theoretical_gc_raw = f['f']
            theoretical_gc_name = f['fn']
        if theoretical_gc_raw is None:
            tgc = getattr(config, 'fastqc_config', {}).get('fastqc_theoretical_gc', None)
            if tgc is not None:
                theoretical_gc_name = os.path.basename(tgc)
                tgc_fn = 'fastqc_theoretical_gc_{}.txt'.format(tgc)
                tgc_path = os.path.join(os.path.dirname(__file__), 'fastqc_theoretical_gc', tgc_fn)
                if not os.path.isfile(tgc_path):
                    tgc_path = tgc
                try:
                    with io.open (tgc_path, "r", encoding='utf-8') as f:
                        theoretical_gc_raw = f.read()
                except IOError:
                    log.warning("Couldn't open FastQC Theoretical GC Content file {}".format(tgc_path))
                    theoretical_gc_raw = None
        if theoretical_gc_raw is not None:
            theoretical_gc = list()
            for l in theoretical_gc_raw.splitlines():
                if '# FastQC theoretical GC content curve:' in l:
                    theoretical_gc_name = l[39:]
                elif not l.startswith('#'):
                    s = l.split()
                    try:
                        theoretical_gc.append([float(s[0]), float(s[1])])
                    except (TypeError, IndexError):
                        pass

        desc = '''The average GC content of reads. Normal random library typically have a
        roughly normal distribution of GC content.'''
        if theoretical_gc is not None:
            # Calculate the count version of the theoretical data based on the largest data store
            max_total = max([sum (d.values()) for d in data.values() ])
            esconfig = {
                'name': 'Theoretical GC Content',
                'dashStyle': 'Dash',
                'lineWidth': 2,
                'color': '#000000',
                'marker': { 'enabled': False },
                'enableMouseTracking': False,
                'showInLegend': False,
            }
            pconfig['extra_series'] = [ [dict(esconfig)], [dict(esconfig)] ]
            pconfig['extra_series'][0][0]['data'] = theoretical_gc
            pconfig['extra_series'][1][0]['data'] = [ [ d[0], (d[1]/100.0)*max_total ] for d in theoretical_gc ]
            desc = " **The dashed black line shows theoretical GC content:** `{}`".format(theoretical_gc_name)

        self.add_section (
            name = 'Per Sequence GC Content',
            anchor = 'fastqc_per_sequence_gc_content',
            description = desc,
            helptext = '''
            From the [FastQC help](http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html):

            _This module measures the GC content across the whole length of each sequence
            in a file and compares it to a modelled normal distribution of GC content._

            _In a normal random library you would expect to see a roughly normal distribution
            of GC content where the central peak corresponds to the overall GC content of
            the underlying genome. Since we don't know the the GC content of the genome the
            modal GC content is calculated from the observed data and used to build a
            reference distribution._

            _An unusually shaped distribution could indicate a contaminated library or
            some other kinds of biased subset. A normal distribution which is shifted
            indicates some systematic bias which is independent of base position. If there
            is a systematic bias which creates a shifted normal distribution then this won't
            be flagged as an error by the module since it doesn't know what your genome's
            GC content should be._
            ''',
            plot = linegraph.plot([data_norm, data], pconfig)
        )