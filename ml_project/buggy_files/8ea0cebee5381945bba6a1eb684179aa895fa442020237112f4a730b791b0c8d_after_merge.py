    def distance(self, q1, q2):
        """Return the undirected distance between qubit q1 to qubit q2."""
        if self.dist is None:
            raise CouplingError("distance has not been computed")
        if q1 not in self.qubits:
            raise CouplingError("%s not in coupling graph" % (q1,))
        if q2 not in self.qubits:
            raise CouplingError("%s not in coupling graph" % (q2,))
        return self.dist[q1][q2]