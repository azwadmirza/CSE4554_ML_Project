    def __init__(self, syslist, connections=[], inplist=[], outlist=[],
                 inputs=None, outputs=None, states=None,
                 params={}, dt=None, name=None):
        """Create an I/O system from a list of systems + connection info.

        The InterconnectedSystem class is used to represent an input/output
        system that consists of an interconnection between a set of subystems.
        The outputs of each subsystem can be summed together to to provide
        inputs to other subsystems.  The overall system inputs and outputs can
        be any subset of subsystem inputs and outputs.

        Parameters
        ----------
        syslist : array_like of InputOutputSystems
            The list of input/output systems to be connected

        connections : tuple of connection specifications, optional
            Description of the internal connections between the subsystems.
            Each element of the tuple describes an input to one of the
            subsystems.  The entries are are of the form:

                (input-spec, output-spec1, output-spec2, ...)

            The input-spec should be a tuple of the form `(subsys_i, inp_j)`
            where `subsys_i` is the index into `syslist` and `inp_j` is the
            index into the input vector for the subsystem.  If `subsys_i` has
            a single input, then the subsystem index `subsys_i` can be listed
            as the input-spec.  If systems and signals are given names, then
            the form 'sys.sig' or ('sys', 'sig') are also recognized.

            Each output-spec should be a tuple of the form `(subsys_i, out_j,
            gain)`.  The input will be constructed by summing the listed
            outputs after multiplying by the gain term.  If the gain term is
            omitted, it is assumed to be 1.  If the system has a single
            output, then the subsystem index `subsys_i` can be listed as the
            input-spec.  If systems and signals are given names, then the form
            'sys.sig', ('sys', 'sig') or ('sys', 'sig', gain) are also
            recognized, and the special form '-sys.sig' can be used to specify
            a signal with gain -1.

            If omitted, the connection map (matrix) can be specified using the
            :func:`~control.InterconnectedSystem.set_connect_map` method.

        inplist : tuple of input specifications, optional
            List of specifications for how the inputs for the overall system
            are mapped to the subsystem inputs.  The input specification is
            the same as the form defined in the connection specification.
            Each system input is added to the input for the listed subsystem.

            If omitted, the input map can be specified using the
            `set_input_map` method.

        outlist : tuple of output specifications, optional
            List of specifications for how the outputs for the subsystems are
            mapped to overall system outputs.  The output specification is the
            same as the form defined in the connection specification
            (including the optional gain term).  Numbered outputs must be
            chosen from the list of subsystem outputs, but named outputs can
            also be contained in the list of subsystem inputs.

            If omitted, the output map can be specified using the
            `set_output_map` method.

        params : dict, optional
            Parameter values for the systems.  Passed to the evaluation
            functions for the system as default values, overriding internal
            defaults.

        dt : timebase, optional
            The timebase for the system, used to specify whether the system is
            operating in continuous or discrete time.  It can have the
            following values:

            * dt = None       No timebase specified
            * dt = 0          Continuous time system
            * dt > 0          Discrete time system with sampling time dt
            * dt = True       Discrete time with unspecified sampling time

        name : string, optional
            System name (used for specifying signals).

        """
        # Convert input and output names to lists if they aren't already
        if not isinstance(inplist, (list, tuple)): inplist = [inplist]
        if not isinstance(outlist, (list, tuple)): outlist = [outlist]

        # Check to make sure all systems are consistent
        self.syslist = syslist
        self.syslist_index = {}
        dt = None
        nstates = 0; self.state_offset = []
        ninputs = 0; self.input_offset = []
        noutputs = 0; self.output_offset = []
        system_count = 0
        for sys in syslist:
            # Make sure time bases are consistent
            if dt is None and sys.dt is not None:
                # Timebase was not specified; set to match this system
                dt = sys.dt
            elif dt != sys.dt:
                raise TypeError("System timebases are not compatible")

            # Make sure number of inputs, outputs, states is given
            if sys.ninputs is None or sys.noutputs is None or \
               sys.nstates is None:
                raise TypeError("System '%s' must define number of inputs, "
                                "outputs, states in order to be connected" %
                                sys)

            # Keep track of the offsets into the states, inputs, outputs
            self.input_offset.append(ninputs)
            self.output_offset.append(noutputs)
            self.state_offset.append(nstates)

            # Keep track of the total number of states, inputs, outputs
            nstates += sys.nstates
            ninputs += sys.ninputs
            noutputs += sys.noutputs

            # Store the index to the system for later retrieval
            # TODO: look for duplicated system names
            self.syslist_index[sys.name] = system_count
            system_count += 1

        # Check for duplicate systems or duplicate names
        sysobj_list = []
        sysname_list = []
        for sys in syslist:
            if sys in sysobj_list:
                warn("Duplicate object found in system list: %s" % str(sys))
            elif sys.name is not None and sys.name in sysname_list:
                warn("Duplicate name found in system list: %s" % sys.name)
            sysobj_list.append(sys)
            sysname_list.append(sys.name)

        # Create the I/O system
        super(InterconnectedSystem, self).__init__(
            inputs=len(inplist), outputs=len(outlist),
            states=nstates, params=params, dt=dt)

        # If input or output list was specified, update it
        nsignals, self.input_index = \
            self._process_signal_list(inputs, prefix='u')
        if nsignals is not None and len(inplist) != nsignals:
            raise ValueError("Wrong number/type of inputs given.")
        nsignals, self.output_index = \
            self._process_signal_list(outputs, prefix='y')
        if nsignals is not None and len(outlist) != nsignals:
            raise ValueError("Wrong number/type of outputs given.")

        # Convert the list of interconnections to a connection map (matrix)
        self.connect_map = np.zeros((ninputs, noutputs))
        for connection in connections:
            input_index = self._parse_input_spec(connection[0])
            for output_spec in connection[1:]:
                output_index, gain = self._parse_output_spec(output_spec)
                self.connect_map[input_index, output_index] = gain

        # Convert the input list to a matrix: maps system to subsystems
        self.input_map = np.zeros((ninputs, self.ninputs))
        for index, inpspec in enumerate(inplist):
            if isinstance(inpspec, (int, str, tuple)): inpspec = [inpspec]
            for spec in inpspec:
                self.input_map[self._parse_input_spec(spec), index] = 1

        # Convert the output list to a matrix: maps subsystems to system
        self.output_map = np.zeros((self.noutputs, noutputs + ninputs))
        for index in range(len(outlist)):
            ylist_index, gain = self._parse_output_spec(outlist[index])
            self.output_map[index, ylist_index] = gain

        # Save the parameters for the system
        self.params = params.copy()