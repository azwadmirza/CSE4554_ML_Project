    def on_link_e2e(self, messages):
        for message in messages:
            circuit = self.exit_sockets[int(message.source[8:])]
            relay_circuit = self.rendezvous_point_for[message.payload.cookie]

            self.remove_exit_socket(circuit.circuit_id, 'linking circuit')
            self.remove_exit_socket(relay_circuit.circuit_id, 'linking circuit')

            self.send_cell([message.candidate], u"linked-e2e", (circuit.circuit_id, message.payload.identifier))

            self.relay_from_to[circuit.circuit_id] = RelayRoute(relay_circuit.circuit_id, relay_circuit.sock_addr, True)
            self.relay_from_to[relay_circuit.circuit_id] = RelayRoute(circuit.circuit_id, circuit.sock_addr, True)