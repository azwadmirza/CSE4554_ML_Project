    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='Peddy', anchor='peddy',
        href='https://github.com/brentp/peddy',
        info="calculates genotype :: pedigree correspondence checks, ancestry checks and sex checks using VCF files.")

        # Find and load any Peddy reports
        self.peddy_data = dict()
        self.peddy_length_counts = dict()
        self.peddy_length_exp = dict()
        self.peddy_length_obsexp = dict()

        # parse peddy summary file
        for f in self.find_log_files('peddy/summary_table'):
            parsed_data = self.parse_peddy_summary(f)
            if parsed_data is not None:
                for s_name in parsed_data:
                    s_name = self.clean_s_name(s_name, f['root'])
                    try:
                        self.peddy_data[s_name].update(parsed_data[s_name])
                    except KeyError:
                        self.peddy_data[s_name] = parsed_data[s_name]

        # parse peddy CSV files
        for pattern in ['het_check', 'ped_check', 'sex_check']:
            sp_key = 'peddy/{}'.format(pattern)
            for f in self.find_log_files(sp_key):
                # some columns have the same name in het_check and sex_check (median_depth)
                # pass pattern to parse_peddy_csv so the column names can include pattern to
                # avoid being overwritten
                parsed_data = self.parse_peddy_csv(f, pattern)
                if parsed_data is not None:
                    for s_name in parsed_data:
                        try:
                            self.peddy_data[s_name].update(parsed_data[s_name])
                        except KeyError:
                            self.peddy_data[s_name] = parsed_data[s_name]

        # parse background PCA JSON file, this is identitical for all peddy runs,
        # so just parse the first one we find
        for f in self.find_log_files("peddy/background_pca"):
            background = json.loads(f['f'])
            PC1 = [x["PC1"] for x in background]
            PC2 = [x["PC2"] for x in background]
            ancestry = [x["ancestry"] for x in background]
            self.peddy_data["background_pca"] =  {
                "PC1": PC1, "PC2": PC2, "ancestry": ancestry}
            break

        # Filter to strip out ignored sample names
        self.peddy_data = self.ignore_samples(self.peddy_data)

        if len(self.peddy_data) == 0:
            raise UserWarning

        log.info("Found {} reports".format(len(self.peddy_data)))

        # Write parsed report data to a file
        self.write_data_file(self.peddy_data, 'multiqc_peddy')

        # Basic Stats Table
        self.peddy_general_stats_table()

        # PCA plot
        self.peddy_pca_plot()

        # Relatedness plot
        self.peddy_relatedness_plot()

        # hetcheck plot
        self.peddy_het_check_plot()

        self.peddy_sex_check_plot()