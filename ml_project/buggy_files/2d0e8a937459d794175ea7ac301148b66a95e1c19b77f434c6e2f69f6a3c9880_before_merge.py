    def _initialize_backend_prop(self):
        """
        Extract readout and CNOT errors and compute swap costs.
        """
        backend_prop = self.backend_prop
        for ginfo in backend_prop.gates:
            if ginfo.gate == 'cx':
                for item in ginfo.parameters:
                    if item.name == 'gate_error':
                        g_reliab = 1.0 - item.value
                        break
                    else:
                        g_reliab = 1.0
                swap_reliab = pow(g_reliab, 3)
                swap_reliab = -math.log(swap_reliab) if swap_reliab != 0 else -math.inf
                self.swap_graph.add_edge(ginfo.qubits[0], ginfo.qubits[1], weight=swap_reliab)
                self.swap_graph.add_edge(ginfo.qubits[1], ginfo.qubits[0], weight=swap_reliab)
                self.cx_errors[(ginfo.qubits[0], ginfo.qubits[1])] = g_reliab
                self.gate_list.append((ginfo.qubits[0], ginfo.qubits[1]))
        idx = 0
        for q in backend_prop.qubits:
            for nduv in q:
                if nduv.name == 'readout_error':
                    self.readout_errors[idx] = 1.0 - nduv.value
                    self.available_hw_qubits.append(idx)
            idx += 1
        for edge in self.cx_errors:
            self.gate_cost[edge] = self.cx_errors[edge] * self.readout_errors[edge[0]] *\
                self.readout_errors[edge[1]]
        self.swap_paths, swap_costs_temp = nx.algorithms.shortest_paths.dense.\
            floyd_warshall_predecessor_and_distance(self.swap_graph, weight='weight')
        for i in swap_costs_temp:
            self.swap_costs[i] = {}
            for j in swap_costs_temp[i]:
                if (i, j) in self.cx_errors:
                    self.swap_costs[i][j] = self.cx_errors[(i, j)]
                elif (j, i) in self.cx_errors:
                    self.swap_costs[i][j] = self.cx_errors[(j, i)]
                else:
                    best_reliab = 0.0
                    for n in self.swap_graph.neighbors(j):
                        if (n, j) in self.cx_errors:
                            reliab = math.exp(-swap_costs_temp[i][n])*self.cx_errors[(n, j)]
                        else:
                            reliab = math.exp(-swap_costs_temp[i][n])*self.cx_errors[(j, n)]
                        if reliab > best_reliab:
                            best_reliab = reliab
                    self.swap_costs[i][j] = best_reliab