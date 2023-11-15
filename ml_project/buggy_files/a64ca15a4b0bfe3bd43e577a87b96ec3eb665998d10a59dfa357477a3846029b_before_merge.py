    def __init__(self):
        # registers
        self.dataset_versions = set()
        self.gene_attribute_names = set()
        self.cell_attribute_names = set()
        self.cell_categorical_attribute_names = set()
        self.attribute_mappings = defaultdict(list)
        self.cell_measurements_col_mappings = dict()

        # initialize attributes
        self._X = None
        self._batch_indices = None
        self._labels = None
        self.n_batches = None
        self.n_labels = None
        self.gene_names = None
        self.cell_types = None
        self.local_means = None
        self.local_vars = None
        self._norm_X = None
        self._corrupted_X = None

        # attributes that should not be set by initialization methods
        self.protected_attributes = ["X"]