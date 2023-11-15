    def _define(self):
        """
        gate sdg a { u1(-pi/2) a; }
        """
        definition = []
        q = QuantumRegister(1, "q")
        rule = [
            (U1Gate(-pi/2), q[0], [])
        ]
        for inst in rule:
            definition.append(inst)
        self.definition = definition