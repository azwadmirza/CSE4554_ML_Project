    def __init__(self, bytecode, pc, nstack, blockstack):
        """
        Parameters
        ----------
        bytecode : numba.bytecode.ByteCode
            function bytecode
        pc : int
            program counter
        nstack : int
            stackdepth at entry
        blockstack : Sequence[Dict]
            A sequence of dictionary denoting entries on the blockstack.
        """
        self._bytecode = bytecode
        self._pc_initial = pc
        self._pc = pc
        self._nstack_initial = nstack
        self._stack = []
        self._blockstack = list(blockstack)
        self._temp_registers = []
        self._insts = []
        self._outedges = []
        self._terminated = False
        self._phis = {}
        self._outgoing_phis = UniqueDict()
        self._used_regs = set()
        for i in range(nstack):
            phi = self.make_temp("phi")
            self._phis[phi] = i
            self.push(phi)