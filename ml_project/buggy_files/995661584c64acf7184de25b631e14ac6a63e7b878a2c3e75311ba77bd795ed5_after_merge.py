    def __add__(sys1, sys2):
        """Add two input/output systems (parallel interconnection)"""
        # TODO: Allow addition of scalars and matrices
        if not isinstance(sys2, InputOutputSystem):
            raise ValueError("Unknown I/O system object ", sys2)
        elif isinstance(sys1, StateSpace) and isinstance(sys2, StateSpace):
            # Special case: maintain linear systems structure
            new_ss_sys = StateSpace.__add__(sys1, sys2)
            # TODO: set input and output names
            new_io_sys = LinearIOSystem(new_ss_sys)

            return new_io_sys

        # Make sure number of input and outputs match
        if sys1.ninputs != sys2.ninputs or sys1.noutputs != sys2.noutputs:
            raise ValueError("Can't add systems with different numbers of "
                             "inputs or outputs.")
        ninputs = sys1.ninputs
        noutputs = sys1.noutputs

        # Create a new system to handle the composition
        newsys = InterconnectedSystem((sys1, sys2))

        # Set up the input map
        newsys.set_input_map(np.concatenate(
            (np.eye(ninputs), np.eye(ninputs)), axis=0))
        # TODO: set up input names

        # Set up the output map
        newsys.set_output_map(np.concatenate(
            (np.eye(noutputs), np.eye(noutputs)), axis=1))
        # TODO: set up output names

        # Return the newly created system
        return newsys