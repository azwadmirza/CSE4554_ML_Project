    def circuit_removed(self, _, __, circuit, additional_info):
        self.session.ipv8.network.remove_by_address(circuit.peer.address)
        if self.log_circuits:
            with open(os.path.join(self.session.config.get_state_dir(), "circuits.log"), 'a') as out_file:
                duration = time.time() - circuit.creation_time
                out_file.write("%d,%f,%d,%d,%s\n" % (circuit.circuit_id, duration, circuit.bytes_up, circuit.bytes_down,
                                                     additional_info))