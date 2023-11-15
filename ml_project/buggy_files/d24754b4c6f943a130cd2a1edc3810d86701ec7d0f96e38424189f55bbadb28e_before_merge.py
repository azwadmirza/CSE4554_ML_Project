    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='QUAST', anchor='quast',
        href="http://quast.bioinf.spbau.ru/",
        info="is a quality assessment tool for genome assemblies, written by " \
             "the Center for Algorithmic Biotechnology.")

        # Get modifiers from config file
        qconfig = getattr(config, "quast_config", {})

        self.contig_length_multiplier = qconfig.get('contig_length_multiplier', 0.001)
        self.contig_length_suffix = qconfig.get('contig_length_suffix', 'Kbp')

        self.total_length_multiplier = qconfig.get('total_length_multiplier', 0.000001)
        self.total_length_suffix = qconfig.get('total_length_suffix', 'Mbp')

        self.total_number_contigs_multiplier = qconfig.get('total_number_contigs_multiplier', 0.001)
        self.total_number_contigs_suffix = qconfig.get('total_number_contigs_suffix', 'K')


        # Find and load any QUAST reports
        self.quast_data = dict()
        for f in self.find_log_files('quast'):
            self.parse_quast_log(f)

        # Filter to strip out ignored sample names
        self.quast_data = self.ignore_samples(self.quast_data)

        if len(self.quast_data) == 0:
            raise UserWarning

        log.info("Found {} reports".format(len(self.quast_data)))

        # Write parsed report data to a file
        self.write_data_file(self.quast_data, 'multiqc_quast')

        # Basic Stats Table
        self.quast_general_stats_table()

        # Quast Stats Table
        self.add_section (
            name = 'Assembly Statistics',
            anchor = 'quast-stats',
            plot = self.quast_table()
        )
        # Number of contigs plot
        self.add_section (
            name = 'Number of Contigs',
            anchor = 'quast-contigs',
            description = """This plot shows the number of contigs found for each assembly, broken
                    down by length.""",
            plot = self.quast_contigs_barplot()
        )
        # Number of genes plot
        ng_pdata = self.quast_predicted_genes_barplot()
        if ng_pdata:
            self.add_section (
                name = 'Number of Predicted Genes',
                anchor = 'quast-genes',
                description = """This plot shows the number of predicted genes found for each
                          assembly, broken down by length.""",
                plot = ng_pdata
            )