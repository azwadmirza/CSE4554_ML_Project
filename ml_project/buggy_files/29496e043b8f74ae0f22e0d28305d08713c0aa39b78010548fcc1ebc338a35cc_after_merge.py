    def __init__(self,
                 kak_basis_gate=None,
                 force_consolidate=False,
                 basis_gates=None):
        """ConsolidateBlocks initializer.

        Args:
            kak_basis_gate (Gate): Basis gate for KAK decomposition.
            force_consolidate (bool): Force block consolidation
            basis_gates (List(str)): Basis gates from which to choose a KAK gate.
        """
        super().__init__()
        self.basis_gates = basis_gates
        self.force_consolidate = force_consolidate

        if kak_basis_gate is not None:
            self.decomposer = TwoQubitBasisDecomposer(kak_basis_gate)
        elif basis_gates is not None:
            kak_basis_gate = unitary_synthesis._choose_kak_gate(basis_gates)
            if kak_basis_gate is not None:
                self.decomposer = TwoQubitBasisDecomposer(kak_basis_gate)
            else:
                self.decomposer = None
        else:
            self.decomposer = TwoQubitBasisDecomposer(CXGate())