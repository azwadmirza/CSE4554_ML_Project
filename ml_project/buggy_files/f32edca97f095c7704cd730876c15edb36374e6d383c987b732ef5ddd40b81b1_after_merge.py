    def __init__(self, args, r=run, p=progress):
        self.args = args
        self.run = r
        self.progress = p

        self.genome_names = []
        self.protein_clusters = {}
        self.protein_clusters_initialized = False
        self.protein_cluster_names = set([])
        self.protein_clusters_gene_alignments = {}
        self.protein_clusters_gene_alignments_available = False
        self.protein_clusters_function_sources = []
        self.protein_clusters_functions_dict = {}
        self.item_orders = {}
        self.views = {}
        self.collection_profile = {}

        self.num_protein_clusters = None
        self.num_genes_in_protein_clusters = None

        self.genomes_storage_is_available = False
        self.genomes_storage_has_functions = False
        self.functions_initialized = False

        try:
            self.pan_db_path = self.args.pan_db
        except:
            self.run.warning('PanSuperclass class called with args without pan_db_path member! Returning prematurely.')
            return

        filesnpaths.is_file_exists(self.pan_db_path)

        self.progress.new('Initializing the pan database superclass')

        self.progress.update('Creating an instance of the pan database')
        pan_db = PanDatabase(self.pan_db_path, run=self.run, progress=self.progress)

        self.progress.update('Setting profile self data dict')
        self.p_meta = pan_db.meta

        self.p_meta['creation_date'] = utils.get_time_to_date(self.p_meta['creation_date']) if 'creation_date' in self.p_meta else 'unknown'
        self.p_meta['genome_names'] = sorted([s.strip() for s in self.p_meta['external_genome_names'].split(',') + self.p_meta['internal_genome_names'].split(',') if s])
        self.p_meta['num_genomes'] = len(self.p_meta['genome_names'])
        self.genome_names = self.p_meta['genome_names']
        self.protein_clusters_gene_alignments_available = self.p_meta['gene_alignments_computed']

        # FIXME: Is this the future where the pan db version is > 6? Great. Then the if statement here no longer
        # needs to check whether 'PCs_ordered' is a valid key in self.p_meta:
        if 'PCs_ordered' in self.p_meta and self.p_meta['PCs_ordered']:
            self.p_meta['available_item_orders'] = sorted([s.strip() for s in self.p_meta['available_item_orders'].split(',')])
            self.item_orders = pan_db.db.get_table_as_dict(t.item_orders_table_name)

            # we need to convert data for 'basic' item orders to array in order to avoid compatibility issues with
            # other additional item orders in pan and full mode (otherwise interactive class gets complicated
            # unnecessarily).
            for item_order in self.item_orders:
                if self.item_orders[item_order]['type'] == 'basic':
                    try:
                        self.item_orders[item_order]['data'] = self.item_orders[item_order]['data'].split(',')
                    except:
                        raise ConfigError("Something is wrong with the basic order `%s` in this pan database :(" % (item_order))
        else:
            self.p_meta['available_item_orders'] = None
            self.p_meta['default_item_order'] = None
            self.item_orders = None

        # recover all protein cluster names so others can access to this information
        # without having to initialize anything
        self.protein_cluster_names = set(pan_db.db.get_single_column_from_table(t.pan_protein_clusters_table_name, 'protein_cluster_id'))

        pan_db.disconnect()

        # create an instance of states table
        self.states_table = TablesForStates(self.pan_db_path)

        self.progress.end()

        if 'genomes_storage' in args.__dict__ and args.genomes_storage:
            self.genomes_storage = auxiliarydataops.GenomesDataStorage(args.genomes_storage,
                                                                       self.p_meta['genomes_storage_hash'],
                                                                       genome_names_to_focus=self.p_meta['genome_names'],
                                                                       run=self.run,
                                                                       progress=self.progress)
            self.genomes_storage_is_available = True
            self.genomes_storage_has_functions = self.genomes_storage.functions_are_available

        self.run.info('Pan DB', 'Initialized: %s (v. %s)' % (self.pan_db_path, anvio.__pan__version__))