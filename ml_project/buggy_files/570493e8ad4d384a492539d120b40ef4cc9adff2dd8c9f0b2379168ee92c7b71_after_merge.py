    def append(self, instruction, qargs=None, cargs=None):
        """Append one or more instructions to the end of the circuit, modifying
        the circuit in place. Expands qargs and cargs.

        Args:
            instruction (Instruction or Operation): Instruction instance to append
            qargs (list(argument)): qubits to attach instruction to
            cargs (list(argument)): clbits to attach instruction to

        Returns:
            Instruction: a handle to the instruction that was just added
        """
        # Convert input to instruction
        if not isinstance(instruction, Instruction) and hasattr(instruction, 'to_instruction'):
            instruction = instruction.to_instruction()

        expanded_qargs = [self.qbit_argument_conversion(qarg) for qarg in qargs or []]
        expanded_cargs = [self.cbit_argument_conversion(carg) for carg in cargs or []]

        instructions = InstructionSet()

        # When broadcasting was handled by decorators (prior to #2282), append
        # received multiple distinct instruction instances, one for each expanded
        # arg. With broadcasting as part of QuantumCircuit.append, the
        # instruction instance is constructed before append is called. However,
        # (at least) ParameterTable expects instruction instances to be unique
        # within a circuit, so make instruction deepcopies for expanded_args[1:].

        first_instruction = True
        for (qarg, carg) in instruction.broadcast_arguments(expanded_qargs, expanded_cargs):
            if first_instruction:
                instructions.add(
                    self._append(instruction, qarg, carg), qarg, carg)
                first_instruction = False
            else:
                instructions.add(
                    self._append(deepcopy(instruction), qarg, carg), qarg, carg)

        return instructions