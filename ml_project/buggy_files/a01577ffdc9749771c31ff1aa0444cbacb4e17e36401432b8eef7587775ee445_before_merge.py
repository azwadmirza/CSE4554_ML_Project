    def __init__(self, backend_prop):
        """
        Chooses a Noise Adaptive Layout

        Args:
            backend_prop (BackendProperties): backend properties object

        Raises:
            TranspilerError: if invalid options
        """
        super().__init__()
        self.backend_prop = backend_prop
        self.swap_graph = nx.DiGraph()
        self.cx_errors = {}
        self.readout_errors = {}
        self.available_hw_qubits = []
        self.gate_list = []
        self.gate_cost = {}
        self.swap_paths = {}
        self.swap_costs = {}
        self.prog_graph = nx.Graph()
        self.qarg_to_id = {}
        self.pending_program_edges = []
        self.prog2hw = {}