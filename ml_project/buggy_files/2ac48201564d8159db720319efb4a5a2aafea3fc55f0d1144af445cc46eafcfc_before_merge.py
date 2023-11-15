    def __init__(self, contigs_db_path, sources=set([]), split_names_of_interest=set([]), init=True, run=run, progress=progress):
        self.run = run
        self.progress = progress

        if not isinstance(sources, type(set([]))):
            raise ConfigError("'sources' variable has to be a set instance.")

        if not isinstance(split_names_of_interest, type(set([]))):
            raise ConfigError("'split_names_of_interest' variable has to be a set instance.")

        self.sources = set([s for s in sources if s])
        self.hmm_hits = {}
        self.hmm_hits_info ={}
        self.hmm_hits_splits = {}
        self.contig_sequences = {}
        self.aa_sequences = {}
        self.genes_in_contigs = {}
        self.splits_in_contigs = {}

        if contigs_db_path:
            self.init_dicts(contigs_db_path, split_names_of_interest)
            self.initialized = True
        else:
            self.initialized = False