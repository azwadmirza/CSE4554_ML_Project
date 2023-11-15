    def run(self, dag):
        """Main run method for the noise adaptive layout."""
        self._initialize_backend_prop()
        num_qubits = self._create_program_graph(dag)
        if num_qubits > len(self.swap_graph):
            raise TranspilerError('Number of qubits greater than device.')
        for end1, end2, _ in sorted(self.prog_graph.edges(data=True),
                                    key=lambda x: x[2]['weight'], reverse=True):
            self.pending_program_edges.append((end1, end2))
        while self.pending_program_edges:
            edge = self._select_next_edge()
            q1_mapped = edge[0] in self.prog2hw
            q2_mapped = edge[1] in self.prog2hw
            if (not q1_mapped) and (not q2_mapped):
                best_hw_edge = self._select_best_remaining_cx()
                self.prog2hw[edge[0]] = best_hw_edge[0]
                self.prog2hw[edge[1]] = best_hw_edge[1]
                self.available_hw_qubits.remove(best_hw_edge[0])
                self.available_hw_qubits.remove(best_hw_edge[1])
            elif not q1_mapped:
                best_hw_qubit = self._select_best_remaining_qubit(edge[0])
                self.prog2hw[edge[0]] = best_hw_qubit
                self.available_hw_qubits.remove(best_hw_qubit)
            else:
                best_hw_qubit = self._select_best_remaining_qubit(edge[1])
                self.prog2hw[edge[1]] = best_hw_qubit
                self.available_hw_qubits.remove(best_hw_qubit)
            new_edges = [x for x in self.pending_program_edges
                         if not (x[0] in self.prog2hw and x[1] in self.prog2hw)]
            self.pending_program_edges = new_edges
        for qid in self.qarg_to_id.values():
            if qid not in self.prog2hw:
                self.prog2hw[qid] = self.available_hw_qubits[0]
                self.available_hw_qubits.remove(self.prog2hw[qid])
        layout = Layout()
        for q in dag.qubits():
            pid = self._qarg_to_id(q)
            hwid = self.prog2hw[pid]
            layout[q] = hwid
        self.property_set['layout'] = layout