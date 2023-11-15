    def parse_fastp_log(self, f):
        """ Parse the JSON output from fastp and save the summary statistics """
        try:
            parsed_json = json.load(f['f'])
        except:
            log.warn("Could not parse fastp JSON: '{}'".format(f['fn']))
            return None

        # Fetch a sample name from the command
        s_name = f['s_name']
        cmd = parsed_json['command'].split()
        for i,v in enumerate(cmd):
            if v == '-i':
                s_name = self.clean_s_name(cmd[i+1], f['root'])
        if s_name == 'fastp':
            log.warn('Could not parse sample name from fastp command: {}'.format(f['fn']))

        self.add_data_source(f, s_name)
        self.fastp_data[s_name] = {}
        self.fastp_duplication_plotdata[s_name] = {}
        self.fastp_insert_size_data[s_name] = {}
        self.fastp_all_data[s_name] = parsed_json
        for k in ['read1_before_filtering','read2_before_filtering','read1_after_filtering','read2_after_filtering']:
            self.fastp_qual_plotdata[k][s_name] = {}
            self.fastp_gc_content_data[k][s_name] = {}
            self.fastp_n_content_data[k][s_name] = {}

        # Parse filtering_result
        try:
            for k in parsed_json['filtering_result']:
                self.fastp_data[s_name]['filtering_result_{}'.format(k)] = float(parsed_json['filtering_result'][k])
        except KeyError:
            log.debug("fastp JSON did not have 'filtering_result' key: '{}'".format(f['fn']))

        # Parse duplication
        try:
            self.fastp_data[s_name]['pct_duplication'] = float(parsed_json['duplication']['rate'] * 100.0)
        except KeyError:
            log.debug("fastp JSON did not have a 'duplication' key: '{}'".format(f['fn']))

        # Parse after_filtering
        try:
            for k in parsed_json['summary']['after_filtering']:
                self.fastp_data[s_name]['after_filtering_{}'.format(k)] = float(parsed_json['summary']['after_filtering'][k])
        except KeyError:
            log.debug("fastp JSON did not have a 'summary'-'after_filtering' keys: '{}'".format(f['fn']))


        # Parse data required to calculate Pct reads surviving
        try:
            self.fastp_data[s_name]['before_filtering_total_reads'] = float(parsed_json['summary']['before_filtering']['total_reads'])
        except KeyError:
            log.debug("Could not find pre-filtering # reads: '{}'".format(f['fn']))

        try:
            self.fastp_data[s_name]['pct_surviving'] = (self.fastp_data[s_name]['after_filtering_total_reads'] / self.fastp_data[s_name]['before_filtering_total_reads']) * 100.0
        except KeyError:
            log.debug("Could not calculate 'pct_surviving': {}".format(f['fn']))

        # Parse adapter_cutting
        try:
            for k in parsed_json['adapter_cutting']:
                try:
                    self.fastp_data[s_name]['adapter_cutting_{}'.format(k)] = float(parsed_json['adapter_cutting'][k])
                except (ValueError, TypeError):
                    pass
        except KeyError:
            log.debug("fastp JSON did not have a 'adapter_cutting' key, skipping: '{}'".format(f['fn']))

        try:
            self.fastp_data[s_name]['pct_adapter'] = (self.fastp_data[s_name]['adapter_cutting_adapter_trimmed_reads'] / self.fastp_data[s_name]['before_filtering_total_reads']) * 100.0
        except KeyError:
            log.debug("Could not calculate 'pct_adapter': {}".format(f['fn']))

        # Duplication rate plot data
        try:
            # First count the total read count in the dup analysis
            total_reads = 0
            for v in parsed_json['duplication']['histogram']:
                total_reads += v
            # Calculate percentages
            for i, v in enumerate(parsed_json['duplication']['histogram']):
                self.fastp_duplication_plotdata[s_name][i+1] = (float(v) / float(total_reads)) * 100.0
        except KeyError:
            log.debug("No duplication rate plot data: {}".format(f['fn']))

        # Insert size plot data
        try:
            # First count the total read count in the insert size analysis
            total_reads = 0
            max_i = 0
            for i, v in enumerate(parsed_json['insert_size']['histogram']):
                total_reads += v
                if float(v) > 0:
                    max_i = i
            # Calculate percentages
            for i, v in enumerate(parsed_json['insert_size']['histogram']):
                if i <= max_i:
                    self.fastp_insert_size_data[s_name][i+1] = (float(v) / float(total_reads)) * 100.0
        except KeyError:
            log.debug("No insert size plot data: {}".format(f['fn']))

        for k in ['read1_before_filtering','read2_before_filtering','read1_after_filtering','read2_after_filtering']:
            # Read quality data
            try:
                for i, v in enumerate(parsed_json[k]['quality_curves']['mean']):
                    self.fastp_qual_plotdata[k][s_name][i+1] = float(v)
            except KeyError:
                log.debug("Read quality {} not found: {}".format(k, f['fn']))

            # GC and N content plots
            try:
                for i, v in enumerate(parsed_json[k]['content_curves']['GC']):
                    self.fastp_gc_content_data[k][s_name][i+1] = float(v) * 100.0
                for i, v in enumerate(parsed_json[k]['content_curves']['N']):
                    self.fastp_n_content_data[k][s_name][i+1] = float(v) * 100.0
            except KeyError:
                log.debug("Content curve data {} not found: {}".format(k, f['fn']))


        # Remove empty dicts
        if len(self.fastp_data[s_name]) == 0:
            del self.fastp_data[s_name]
        if len(self.fastp_duplication_plotdata[s_name]) == 0:
            del self.fastp_duplication_plotdata[s_name]
        if len(self.fastp_insert_size_data[s_name]) == 0:
            del self.fastp_insert_size_data[s_name]
        if len(self.fastp_all_data[s_name]) == 0:
            del self.fastp_all_data[s_name]