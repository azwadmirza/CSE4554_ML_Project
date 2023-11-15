    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(
            name="Kraken",
            anchor="kraken",
            href="https://ccb.jhu.edu/software/kraken/",
            info="is a taxonomic classification tool that uses exact k-mer matches to find the lowest common ancestor (LCA) of a given sequence.",
        )

        self.t_ranks = OrderedDict()
        self.t_ranks["S"] = "Species"
        self.t_ranks["G"] = "Genus"
        self.t_ranks["F"] = "Family"
        self.t_ranks["O"] = "Order"
        self.t_ranks["C"] = "Class"
        self.t_ranks["P"] = "Phylum"
        self.t_ranks["K"] = "Kingdom"
        self.t_ranks["D"] = "Domain"
        self.t_ranks["R"] = "Root"
        # self.t_ranks['U'] = 'Unclassified'

        # Find and load any kraken reports
        self.kraken_raw_data = dict()
        for f in self.find_log_files("kraken", filehandles=True):
            self.parse_logs(f)

        # Filter to strip out ignored sample names
        self.kraken_raw_data = self.ignore_samples(self.kraken_raw_data)

        if len(self.kraken_raw_data) == 0:
            raise UserWarning

        log.info("Found {} reports".format(len(self.kraken_raw_data)))

        # Sum counts across all samples, so that we can pick top 5
        self.kraken_total_pct = dict()
        self.kraken_total_counts = dict()
        self.kraken_sample_total_readcounts = dict()
        self.sum_sample_counts()

        self.general_stats_cols()
        self.top_five_barplot()