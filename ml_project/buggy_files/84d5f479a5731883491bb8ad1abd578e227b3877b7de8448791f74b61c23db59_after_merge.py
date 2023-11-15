    def wire_names(self, with_initial_state=False):
        """Returns a list of names for each wire.

        Args:
            with_initial_state (bool): Optional (Default: False). If true, adds
                the initial value to the name.

        Returns:
            List: The list of wire names.
        """
        if with_initial_state:
            initial_qubit_value = '|0>'
            initial_clbit_value = '0 '
        else:
            initial_qubit_value = ''
            initial_clbit_value = ''

        qubit_labels = []
        if self.layout is None:
            for bit in self.qregs:
                label = '{name}_{index}: ' + initial_qubit_value
                qubit_labels.append(label.format(name=bit.register.name,
                                                 index=bit.index,
                                                 physical=''))
        else:
            for bit in self.qregs:
                if self.layout[bit.index]:
                    label = '{name}_{index} -> {physical} ' + initial_qubit_value
                    qubit_labels.append(label.format(name=self.layout[bit.index].register.name,
                                                     index=self.layout[bit.index].index,
                                                     physical=bit.index))
                else:
                    qubit_labels.append('%s ' % bit.index + initial_qubit_value)

        clbit_labels = []
        previous_creg = None
        for bit in self.cregs:
            if self.cregbundle:
                if previous_creg == bit.register:
                    continue
                previous_creg = bit.register
                label = '{name}: {initial_value}{size}/'
                clbit_labels.append(label.format(name=bit.register.name,
                                                 initial_value=initial_clbit_value,
                                                 size=bit.register.size))
            else:
                label = '{name}_{index}: ' + initial_clbit_value
                clbit_labels.append(label.format(name=bit.register.name, index=bit.index))
        return qubit_labels + clbit_labels