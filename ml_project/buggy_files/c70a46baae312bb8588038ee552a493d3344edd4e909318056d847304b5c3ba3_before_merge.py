    def qasm(self, decls_only=False, add_swap=False,
             no_decls=False, qeflag=False, aliases=None, eval_symbols=False):
        """Return a string containing QASM for this circuit.

        if qeflag is True, add a line to include "qelib1.inc"
        and only generate gate code for gates not in qelib1.

        if eval_symbols is True, evaluate all symbolic
        expressions to their floating point representation.

        if no_decls is True, only print the instructions.

        if aliases is not None, aliases contains a dict mapping
        the current qubits in the circuit to new qubit names.
        We will deduce the register names and sizes from aliases.

        if decls_only is True, only print the declarations.

        if add_swap is True, add the definition of swap in terms of
        cx if necessary.
        """
        # TODO: some of the input flags are not needed anymore
        # Rename qregs if necessary
        if aliases:
            qregdata = {}
            for q in aliases.values():
                if q[0] not in qregdata:
                    qregdata[q[0]] = q[1] + 1
                elif qregdata[q[0]] < q[1] + 1:
                    qregdata[q[0]] = q[1] + 1
        else:
            qregdata = self.qregs
        # Write top matter
        if no_decls:
            out = ""
        else:
            printed_gates = []
            out = "OPENQASM 2.0;\n"
            if qeflag:
                out += "include \"qelib1.inc\";\n"
            for k, v in sorted(qregdata.items()):
                out += "qreg %s[%d];\n" % (k, v.size)
            for k, v in sorted(self.cregs.items()):
                out += "creg %s[%d];\n" % (k, v.size)
            omit = ["U", "CX", "measure", "reset", "barrier"]
            # TODO: dagcircuit shouldn't know about extensions
            if qeflag:
                qelib = ["u3", "u2", "u1", "cx", "id", "x", "y", "z", "h",
                         "s", "sdg", "t", "tdg", "cz", "cy", "ccx", "cu1",
                         "cu3", "swap", "cswap", "u0", "rx", "ry", "rz",
                         "ch", "crz", "rzz"]
                omit.extend(qelib)
                printed_gates.extend(qelib)
            simulator_instructions = ["snapshot", "save", "load", "noise", "wait"]
            omit.extend(simulator_instructions)
            for k in self.basis.keys():
                if k not in omit:
                    if not self.gates[k]["opaque"]:
                        calls = self.gates[k]["body"].calls()
                        for c in calls:
                            if c not in printed_gates:
                                out += self._gate_string(c) + "\n"
                                printed_gates.append(c)
                    if k not in printed_gates:
                        out += self._gate_string(k) + "\n"
                        printed_gates.append(k)
            if add_swap and not qeflag and "cx" not in self.basis:
                out += "gate cx a,b { CX a,b; }\n"
            if add_swap and "swap" not in self.basis:
                out += "gate swap a,b { cx a,b; cx b,a; cx a,b; }\n"
        # Write the instructions
        if not decls_only:
            for n in nx.lexicographical_topological_sort(self.multi_graph):
                nd = self.multi_graph.node[n]
                if nd["type"] == "op":
                    if nd["condition"] is not None:
                        out += "if(%s==%d) " \
                               % (nd["condition"][0], nd["condition"][1])
                    if not nd["cargs"]:
                        nm = nd["name"]
                        if aliases:
                            qarglist = map(lambda x: aliases[x], nd["qargs"])
                        else:
                            qarglist = nd["qargs"]
                        qarg = ",".join(map(lambda x: "%s[%d]" % (x[0], x[1]),
                                            qarglist))
                        if nd["params"]:
                            if eval_symbols:
                                param = ",".join(map(lambda x: str(sympy.N(x)),
                                                     nd["params"]))
                            else:
                                param = ",".join(map(lambda x: x.replace("**", "^"),
                                                     map(str, nd["params"])))
                            out += "%s(%s) %s;\n" % (nm, param, qarg)
                        else:
                            out += "%s %s;\n" % (nm, qarg)
                    else:
                        if nd["name"] == "measure":
                            if len(nd["cargs"]) != 1 or len(nd["qargs"]) != 1 \
                                    or nd["params"]:
                                raise QISKitError("bad node data")

                            qname = nd["qargs"][0][0]
                            qindex = nd["qargs"][0][1]
                            if aliases:
                                newq = aliases[(qname, qindex)]
                                qname = newq[0]
                                qindex = newq[1]
                            out += "measure %s[%d] -> %s[%d];\n" \
                                   % (qname,
                                      qindex,
                                      nd["cargs"][0][0],
                                      nd["cargs"][0][1])
                        else:
                            raise QISKitError("bad node data")

        return out