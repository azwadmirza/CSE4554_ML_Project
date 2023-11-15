    def circuit_dead(self, broken_circuit):
        """
        When a circuit dies, we update the destinations dictionary and remove all peers that are affected.
        """
        counter = 0
        affected_destinations = set()
        for hops, destinations in list(self.destinations.items()):
            new_affected_destinations = set(destination for destination, tunnel_circuit in list(destinations.items())
                                            if tunnel_circuit == broken_circuit)
            for destination in new_affected_destinations:
                if destination in self.destinations[hops]:
                    del self.destinations[hops][destination]
                    counter += 1

            affected_destinations.update(new_affected_destinations)

        if counter > 0:
            self._logger.debug("Deleted %d peers from destination list", counter)

        if broken_circuit.circuit_id in self.circuit_id_to_connection:
            self.circuit_id_to_connection.pop(broken_circuit.circuit_id, None)

        return affected_destinations