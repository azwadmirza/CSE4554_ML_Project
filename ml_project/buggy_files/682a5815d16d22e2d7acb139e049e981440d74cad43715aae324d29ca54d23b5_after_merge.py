    def __init__(self,
                 num_qubits: Optional[int] = None,
                 rotation_blocks: Optional[Union[QuantumCircuit, List[QuantumCircuit],
                                                 Instruction, List[Instruction]]] = None,
                 entanglement_blocks: Optional[Union[QuantumCircuit, List[QuantumCircuit],
                                                     Instruction, List[Instruction]]] = None,
                 entanglement: Optional[Union[List[int], List[List[int]]]] = None,
                 reps: int = 1,
                 insert_barriers: bool = False,
                 parameter_prefix: str = 'θ',
                 overwrite_block_parameters: Union[bool, List[List[Parameter]]] = True,
                 skip_final_rotation_layer: bool = False,
                 skip_unentangled_qubits: bool = False,
                 initial_state: Optional[Any] = None,
                 name: Optional[str] = 'nlocal') -> None:
        """Create a new n-local circuit.

        Args:
            num_qubits: The number of qubits of the circuit.
            rotation_blocks: The blocks used in the rotation layers. If multiple are passed,
                these will be applied one after another (like new sub-layers).
            entanglement_blocks: The blocks used in the entanglement layers. If multiple are passed,
                these will be applied one after another. To use different enganglements for
                the sub-layers, see :meth:`get_entangler_map`.
            entanglement: The indices specifying on which qubits the input blocks act. If None, the
                entanglement blocks are applied at the top of the circuit.
            reps: Specifies how often the rotation blocks and entanglement blocks are repeated.
            insert_barriers: If True, barriers are inserted in between each layer. If False,
                no barriers are inserted.
            parameter_prefix: The prefix used if default parameters are generated.
            overwrite_block_parameters: If the parameters in the added blocks should be overwritten.
                If False, the parameters in the blocks are not changed.
            skip_final_rotation_layer: Whether a final rotation layer is added to the circuit.
            skip_unentangled_qubits: If ``True``, the rotation gates act only on qubits that
                are entangled. If ``False``, the rotation gates act on all qubits.
            initial_state: A `qiskit.aqua.components.initial_states.InitialState` object which can
                be used to describe an initial state prepended to the NLocal circuit. This
                is primarily for compatibility with algorithms in Qiskit Aqua, which leverage
                this object to prepare input states.
            name: The name of the circuit.

        Examples:
            TODO

        Raises:
            ImportError: If an ``initial_state`` is specified but Qiskit Aqua is not installed.
            TypeError: If an ``initial_state`` is specified but not of the correct type,
                ``qiskit.aqua.components.initial_states.InitialState``.
            ValueError: If reps parameter is less than or equal to 0.
        """
        super().__init__(name=name)

        self._num_qubits = None
        self._insert_barriers = insert_barriers
        self._reps = reps
        self._entanglement_blocks = []
        self._rotation_blocks = []
        self._prepended_blocks = []
        self._prepended_entanglement = []
        self._appended_blocks = []
        self._appended_entanglement = []
        self._entanglement = None
        self._entangler_maps = None
        self._ordered_parameters = ParameterVector(name=parameter_prefix)
        self._overwrite_block_parameters = overwrite_block_parameters
        self._skip_final_rotation_layer = skip_final_rotation_layer
        self._skip_unentangled_qubits = skip_unentangled_qubits
        self._initial_state, self._initial_state_circuit = None, None
        self._data = None
        self._bounds = None

        if reps <= 0:
            raise ValueError('The value of reps should be larger than or equal to 1')

        if num_qubits is not None:
            self.num_qubits = num_qubits

        if entanglement_blocks is not None:
            self.entanglement_blocks = entanglement_blocks

        if rotation_blocks is not None:
            self.rotation_blocks = rotation_blocks

        if entanglement is not None:
            self.entanglement = entanglement

        if initial_state is not None:
            try:
                from qiskit.aqua.components.initial_states import InitialState
                if not isinstance(initial_state, InitialState):
                    raise TypeError('initial_state must be of type InitialState, but is '
                                    '{}.'.format(type(initial_state)))
            except ImportError:
                raise ImportError('Could not import the qiskit.aqua.components.initial_states.'
                                  'InitialState. To use this feature Qiskit Aqua must be installed.'
                                  )
            self.initial_state = initial_state