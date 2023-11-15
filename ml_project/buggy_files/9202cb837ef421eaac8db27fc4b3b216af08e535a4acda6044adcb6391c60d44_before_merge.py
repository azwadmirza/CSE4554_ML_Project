    def _build_latex_array(self, aliases=None):
        """Returns an array of strings containing \\LaTeX for this circuit.

        If aliases is not None, aliases contains a dict mapping
        the current qubits in the circuit to new qubit names.
        We will deduce the register names and sizes from aliases.
        """

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

        column = 1
        # Leave a column to display number of classical registers if needed
        if self.cregbundle and self.ops[0][0].name == "measure":
            column += 1
        for layer in self.ops:
            num_cols_used = 1

            for op in layer:
                if op.condition:
                    mask = self._get_mask(op.condition[0])
                    cl_reg = self.clbit_list[self._ffs(mask)]
                    if_reg = cl_reg.register
                    pos_2 = self.img_regs[cl_reg]
                    if_value = format(op.condition[1],
                                      'b').zfill(self.cregs[if_reg])[::-1]
                if isinstance(op.op, ControlledGate) and op.name not in [
                        'ccx', 'cx', 'cz', 'cu1', 'cu3', 'crz',
                        'cswap']:
                    qarglist = op.qargs
                    name = generate_latex_label(
                        op.op.base_gate.name.upper()).replace(" ", "\\,")
                    pos_array = []
                    num_ctrl_qubits = op.op.num_ctrl_qubits
                    num_qargs = len(qarglist) - num_ctrl_qubits
                    for ctrl in range(len(qarglist)):
                        pos_array.append(self.img_regs[qarglist[ctrl]])
                    pos_qargs = pos_array[num_ctrl_qubits:]
                    ctrl_pos = pos_array[:num_ctrl_qubits]
                    ctrl_state = "{0:b}".format(op.op.ctrl_state).rjust(num_ctrl_qubits, '0')[::-1]
                    if op.condition:
                        mask = self._get_mask(op.condition[0])
                        cl_reg = self.clbit_list[self._ffs(mask)]
                        if_reg = cl_reg.register
                        pos_cond = self.img_regs[if_reg[0]]
                        temp = pos_array + [pos_cond]
                        temp.sort(key=int)
                        bottom = temp[len(pos_array) - 1]
                        gap = pos_cond - bottom
                        for i in range(self.cregs[if_reg]):
                            if if_value[i] == '1':
                                self._latex[pos_cond + i][column] = \
                                    "\\control \\cw \\cwx[-" + str(gap) + "]"
                                gap = 1
                            else:
                                self._latex[pos_cond + i][column] = \
                                    "\\controlo \\cw \\cwx[-" + str(gap) + "]"
                                gap = 1
                    if num_qargs == 1:
                        for index, ctrl_item in enumerate(zip(ctrl_pos, ctrl_state)):
                            pos = ctrl_item[0]
                            cond = ctrl_item[1]
                            nxt = pos_array[index]
                            if pos_array[index] > pos_array[-1]:
                                nxt -= 1
                                while nxt not in pos_array:
                                    nxt -= 1
                            else:
                                nxt += 1
                                while nxt not in pos_array:
                                    nxt += 1
                            if cond == '0':
                                self._latex[pos][column] = "\\ctrlo{" + str(
                                    nxt - pos_array[index]) + "}"
                            elif cond == '1':
                                self._latex[pos][column] = "\\ctrl{" + str(
                                    nxt - pos_array[index]) + "}"
                        if name == 'Z':
                            self._latex[pos_array[-1]][column] = "\\control\\qw"
                        else:
                            self._latex[pos_array[-1]][column] = "\\gate{%s}" % name
                    else:
                        pos_start = min(pos_qargs)
                        pos_stop = max(pos_qargs)
                        # If any controls appear in the span of the multiqubit
                        # gate just treat the whole thing as a big gate instead
                        # of trying to render the controls separately
                        if any(ctrl_pos) in range(pos_start, pos_stop):
                            pos_start = min(pos_array)
                            pos_stop = max(pos_array)
                            num_qargs = len(qarglist)
                            name = generate_latex_label(
                                op.name).replace(" ", "\\,")
                        else:
                            for index, ctrl_item in enumerate(zip(ctrl_pos, ctrl_state)):
                                pos = ctrl_item[0]
                                cond = ctrl_item[1]
                                if index + 1 >= num_ctrl_qubits:
                                    if pos_array[index] > pos_stop:
                                        upper = pos_stop
                                    else:
                                        upper = pos_start
                                else:
                                    upper = pos_array[index + 1]

                                if cond == '0':
                                    self._latex[pos][column] = "\\ctrlo{" + str(
                                        upper - pos_array[index]) + "}"
                                elif cond == '1':
                                    self._latex[pos][column] = "\\ctrl{" + str(
                                        upper - pos_array[index]) + "}"

                        self._latex[pos_start][column] = ("\\multigate{%s}{%s}" %
                                                          (num_qargs - 1, name))
                        for pos in range(pos_start + 1, pos_stop + 1):
                            self._latex[pos][column] = ("\\ghost{%s}" % name)

                elif op.name not in ['measure', 'barrier', 'snapshot', 'load',
                                     'save', 'noise']:
                    nm = generate_latex_label(op.name).replace(" ", "\\,")
                    qarglist = op.qargs
                    if aliases is not None:
                        qarglist = map(lambda x: aliases[x], qarglist)
                    if len(qarglist) == 1:
                        pos_1 = self.img_regs[qarglist[0]]

                        if op.condition:
                            mask = self._get_mask(op.condition[0])
                            cl_reg = self.clbit_list[self._ffs(mask)]
                            if_reg = cl_reg.register
                            pos_2 = self.img_regs[cl_reg]

                            if nm == "x":
                                self._latex[pos_1][column] = "\\gate{X}"
                            elif nm == "y":
                                self._latex[pos_1][column] = "\\gate{Y}"
                            elif nm == "z":
                                self._latex[pos_1][column] = "\\gate{Z}"
                            elif nm == "h":
                                self._latex[pos_1][column] = "\\gate{H}"
                            elif nm == "s":
                                self._latex[pos_1][column] = "\\gate{S}"
                            elif nm == "sdg":
                                self._latex[pos_1][column] = "\\gate{S^\\dag}"
                            elif nm == "t":
                                self._latex[pos_1][column] = "\\gate{T}"
                            elif nm == "tdg":
                                self._latex[pos_1][column] = "\\gate{T^\\dag}"
                            elif nm == "u0":
                                self._latex[pos_1][column] = "\\gate{U_0(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "u1":
                                self._latex[pos_1][column] = "\\gate{U_1(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "u2":
                                self._latex[pos_1][column] = \
                                    "\\gate{U_2\\left(%s,%s\\right)}" % (
                                        self.parse_params(op.op.params[0]),
                                        self.parse_params(op.op.params[1]))
                            elif nm == "u3":
                                self._latex[pos_1][column] = ("\\gate{U_3(%s,%s,%s)}" % (
                                    self.parse_params(op.op.params[0]),
                                    self.parse_params(op.op.params[1]),
                                    self.parse_params(op.op.params[2])))
                            elif nm == "rx":
                                self._latex[pos_1][column] = "\\gate{R_x(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "ry":
                                self._latex[pos_1][column] = "\\gate{R_y(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "rz":
                                self._latex[pos_1][column] = "\\gate{R_z(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            else:
                                self._latex[pos_1][column] = ("\\gate{%s}" % nm)

                            gap = pos_2 - pos_1
                            for i in range(self.cregs[if_reg]):
                                if if_value[i] == '1':
                                    self._latex[pos_2 + i][column] = \
                                        "\\control \\cw \\cwx[-" + str(gap) + "]"
                                    gap = 1
                                else:
                                    self._latex[pos_2 + i][column] = \
                                        "\\controlo \\cw \\cwx[-" + str(gap) + "]"
                                    gap = 1

                        else:
                            if nm == "x":
                                self._latex[pos_1][column] = "\\gate{X}"
                            elif nm == "y":
                                self._latex[pos_1][column] = "\\gate{Y}"
                            elif nm == "z":
                                self._latex[pos_1][column] = "\\gate{Z}"
                            elif nm == "h":
                                self._latex[pos_1][column] = "\\gate{H}"
                            elif nm == "s":
                                self._latex[pos_1][column] = "\\gate{S}"
                            elif nm == "sdg":
                                self._latex[pos_1][column] = "\\gate{S^\\dag}"
                            elif nm == "t":
                                self._latex[pos_1][column] = "\\gate{T}"
                            elif nm == "tdg":
                                self._latex[pos_1][column] = "\\gate{T^\\dag}"
                            elif nm == "u0":
                                self._latex[pos_1][column] = "\\gate{U_0(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "u1":
                                self._latex[pos_1][column] = "\\gate{U_1(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "u2":
                                self._latex[pos_1][column] = \
                                    "\\gate{U_2\\left(%s,%s\\right)}" % (
                                        self.parse_params(op.op.params[0]),
                                        self.parse_params(op.op.params[1]))
                            elif nm == "u3":
                                self._latex[pos_1][column] = ("\\gate{U_3(%s,%s,%s)}" % (
                                    self.parse_params(op.op.params[0]),
                                    self.parse_params(op.op.params[1]),
                                    self.parse_params(op.op.params[2])))
                            elif nm == "rx":
                                self._latex[pos_1][column] = "\\gate{R_x(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "ry":
                                self._latex[pos_1][column] = "\\gate{R_y(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "rz":
                                self._latex[pos_1][column] = "\\gate{R_z(%s)}" % (
                                    self.parse_params(op.op.params[0]))
                            elif nm == "reset":
                                self._latex[pos_1][column] = (
                                    "\\push{\\rule{.6em}{0em}\\ket{0}\\"
                                    "rule{.2em}{0em}} \\qw")
                            else:
                                self._latex[pos_1][column] = ("\\gate{%s}" % nm)

                    elif len(qarglist) == 2:
                        if isinstance(op.op, ControlledGate):
                            cond = str(op.op.ctrl_state)
                        pos_1 = self.img_regs[qarglist[0]]
                        pos_2 = self.img_regs[qarglist[1]]

                        if op.condition:
                            pos_3 = self.img_regs[if_reg[0]]
                            temp = [pos_1, pos_2, pos_3]
                            temp.sort(key=int)
                            bottom = temp[1]

                            gap = pos_3 - bottom
                            for i in range(self.cregs[if_reg]):
                                if if_value[i] == '1':
                                    self._latex[pos_3 + i][column] = \
                                        "\\control \\cw \\cwx[-" + str(gap) + "]"
                                    gap = 1
                                else:
                                    self._latex[pos_3 + i][column] = \
                                        "\\controlo \\cw \\cwx[-" + str(gap) + "]"
                                    gap = 1

                            if nm == "cx":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\targ"
                            elif nm == "cz":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\control\\qw"
                            elif nm == "cy":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\gate{Y}"
                            elif nm == "ch":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\gate{H}"
                            elif nm == "swap":
                                self._latex[pos_1][column] = "\\qswap"
                                self._latex[pos_2][column] = \
                                    "\\qswap \\qwx[" + str(pos_1 - pos_2) + "]"
                            elif nm == "crz":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = \
                                    "\\gate{R_z(%s)}" % (self.parse_params(op.op.params[0]))
                            elif nm == "cu1":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\control \\qw"
                                self._latex[min(pos_1, pos_2)][column + 1] = \
                                    "\\dstick{%s}\\qw" % (self.parse_params(op.op.params[0]))
                                self._latex[max(pos_1, pos_2)][column + 1] = "\\qw"
                                # this is because this gate takes up 2 columns,
                                # and we have just written to the next column
                                num_cols_used = 2
                            elif nm == "cu3":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = \
                                    "\\gate{U_3(%s,%s,%s)}" % \
                                    (self.parse_params(op.op.params[0]),
                                     self.parse_params(op.op.params[1]),
                                     self.parse_params(op.op.params[2]))
                            elif nm == "rzz":
                                self._latex[pos_1][column] = "\\ctrl{" + str(
                                    pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\control \\qw"
                                # Based on the \cds command of the qcircuit package
                                self._latex[min(pos_1, pos_2)][column + 1] = \
                                    "*+<0em,0em>{\\hphantom{zz()}} \\POS [0,0].[%d,0]=" \
                                    "\"e\",!C *{zz(%s)};\"e\"+ R \\qw" % \
                                    (max(pos_1, pos_2), self.parse_params(op.op.params[0]))
                                self._latex[max(pos_1, pos_2)][column + 1] = "\\qw"
                                num_cols_used = 2
                        else:
                            temp = [pos_1, pos_2]
                            temp.sort(key=int)

                            if nm == "cx":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\targ"
                            elif nm == "cz":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\control\\qw"
                            elif nm == "cy":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\gate{Y}"
                            elif nm == "ch":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\gate{H}"
                            elif nm == "swap":
                                self._latex[pos_1][column] = "\\qswap"
                                self._latex[pos_2][column] = \
                                    "\\qswap \\qwx[" + str(pos_1 - pos_2) + "]"
                            elif nm == "crz":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = \
                                    "\\gate{R_z(%s)}" % (self.parse_params(op.op.params[0]))
                            elif nm == "cu1":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\control \\qw"
                                self._latex[min(pos_1, pos_2)][column + 1] = \
                                    "\\dstick{%s}\\qw" % (self.parse_params(op.op.params[0]))
                                self._latex[max(pos_1, pos_2)][column + 1] = "\\qw"
                                num_cols_used = 2
                            elif nm == "cu3":
                                if cond == '0':
                                    self._latex[pos_1][column] = \
                                        "\\ctrlo{" + str(pos_2 - pos_1) + "}"
                                elif cond == '1':
                                    self._latex[pos_1][column] = \
                                        "\\ctrl{" + str(pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = \
                                    ("\\gate{U_3(%s,%s,%s)}" %
                                     (self.parse_params(op.op.params[0]),
                                      self.parse_params(op.op.params[1]),
                                      self.parse_params(op.op.params[2])))
                            elif nm == "rzz":
                                self._latex[pos_1][column] = "\\ctrl{" + str(
                                    pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\control \\qw"
                                # Based on the \cds command of the qcircuit package
                                self._latex[min(pos_1, pos_2)][column + 1] = \
                                    "*+<0em,0em>{\\hphantom{zz()}} \\POS [0,0].[%d,0]=" \
                                    "\"e\",!C *{zz(%s)};\"e\"+ R \\qw" % \
                                    (max(pos_1, pos_2), self.parse_params(op.op.params[0]))
                                self._latex[max(pos_1, pos_2)][column + 1] = "\\qw"
                                num_cols_used = 2
                            else:
                                start_pos = min([pos_1, pos_2])
                                stop_pos = max([pos_1, pos_2])
                                if stop_pos - start_pos >= 2:
                                    delta = stop_pos - start_pos
                                    self._latex[start_pos][column] = ("\\multigate{%s}{%s}"
                                                                      % (delta, nm))
                                    for i_pos in range(start_pos + 1, stop_pos + 1):
                                        self._latex[i_pos][column] = ("\\ghost{%s}"
                                                                      % nm)
                                else:
                                    self._latex[start_pos][column] = ("\\multigate{1}{%s}"
                                                                      % nm)
                                    self._latex[stop_pos][column] = ("\\ghost{%s}" %
                                                                     nm)

                    elif len(qarglist) == 3:
                        if isinstance(op.op, ControlledGate):
                            ctrl_state = "{0:b}".format(op.op.ctrl_state).rjust(2, '0')[::-1]
                            cond_1 = ctrl_state[0]
                            cond_2 = ctrl_state[1]
                        pos_1 = self.img_regs[qarglist[0]]
                        pos_2 = self.img_regs[qarglist[1]]
                        pos_3 = self.img_regs[qarglist[2]]

                        if op.condition:
                            pos_4 = self.img_regs[if_reg[0]]
                            temp = [pos_1, pos_2, pos_3, pos_4]
                            temp.sort(key=int)
                            bottom = temp[2]

                            gap = pos_4 - bottom
                            for i in range(self.cregs[if_reg]):
                                if if_value[i] == '1':
                                    self._latex[pos_4 + i][column] = \
                                        "\\control \\cw \\cwx[-" + str(gap) + "]"
                                    gap = 1
                                else:
                                    self._latex[pos_4 + i][column] = \
                                        "\\controlo \\cw \\cwx[-" + str(gap) + "]"
                                    gap = 1

                            if nm == "ccx":
                                if cond_1 == '0':
                                    self._latex[pos_1][column] = "\\ctrlo{" + str(
                                        pos_2 - pos_1) + "}"
                                elif cond_1 == '1':
                                    self._latex[pos_1][column] = "\\ctrl{" + str(
                                        pos_2 - pos_1) + "}"
                                if cond_2 == '0':
                                    self._latex[pos_2][column] = "\\ctrlo{" + str(
                                        pos_3 - pos_2) + "}"
                                elif cond_2 == '1':
                                    self._latex[pos_2][column] = "\\ctrl{" + str(
                                        pos_3 - pos_2) + "}"
                                self._latex[pos_3][column] = "\\targ"

                            if nm == "cswap":
                                if cond_1 == '0':
                                    self._latex[pos_1][column] = "\\ctrlo{" + str(
                                        pos_2 - pos_1) + "}"
                                elif cond_1 == '1':
                                    self._latex[pos_1][column] = "\\ctrl{" + str(
                                        pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\qswap"
                                self._latex[pos_3][column] = \
                                    "\\qswap \\qwx[" + str(pos_2 - pos_3) + "]"
                        else:
                            if nm == "ccx":
                                if cond_1 == '0':
                                    self._latex[pos_1][column] = "\\ctrlo{" + str(
                                        pos_2 - pos_1) + "}"
                                elif cond_1 == '1':
                                    self._latex[pos_1][column] = "\\ctrl{" + str(
                                        pos_2 - pos_1) + "}"
                                if cond_2 == '0':
                                    self._latex[pos_2][column] = "\\ctrlo{" + str(
                                        pos_3 - pos_2) + "}"
                                elif cond_2 == '1':
                                    self._latex[pos_2][column] = "\\ctrl{" + str(
                                        pos_3 - pos_2) + "}"
                                self._latex[pos_3][column] = "\\targ"

                            elif nm == "cswap":
                                if cond_1 == '0':
                                    self._latex[pos_1][column] = "\\ctrlo{" + str(
                                        pos_2 - pos_1) + "}"
                                elif cond_1 == '1':
                                    self._latex[pos_1][column] = "\\ctrl{" + str(
                                        pos_2 - pos_1) + "}"
                                self._latex[pos_2][column] = "\\qswap"
                                self._latex[pos_3][column] = \
                                    "\\qswap \\qwx[" + str(pos_2 - pos_3) + "]"
                            else:
                                start_pos = min([pos_1, pos_2, pos_3])
                                stop_pos = max([pos_1, pos_2, pos_3])
                                if stop_pos - start_pos >= 3:
                                    delta = stop_pos - start_pos
                                    self._latex[start_pos][column] = ("\\multigate{%s}{%s}" %
                                                                      (delta, nm))
                                    for i_pos in range(start_pos + 1, stop_pos + 1):
                                        self._latex[i_pos][column] = ("\\ghost{%s}" %
                                                                      nm)
                                else:
                                    self._latex[pos_1][column] = ("\\multigate{2}{%s}" %
                                                                  nm)
                                    self._latex[pos_2][column] = ("\\ghost{%s}" %
                                                                  nm)
                                    self._latex[pos_3][column] = ("\\ghost{%s}" %
                                                                  nm)

                    elif len(qarglist) > 3:
                        nbits = len(qarglist)
                        pos_array = [self.img_regs[qarglist[0]]]
                        for i in range(1, nbits):
                            pos_array.append(self.img_regs[qarglist[i]])
                        pos_start = min(pos_array)
                        pos_stop = max(pos_array)
                        self._latex[pos_start][column] = ("\\multigate{%s}{%s}" %
                                                          (nbits - 1, nm))
                        for pos in range(pos_start + 1, pos_stop + 1):
                            self._latex[pos][column] = ("\\ghost{%s}" % nm)

                elif op.name == "measure":
                    if (len(op.cargs) != 1
                            or len(op.qargs) != 1
                            or op.op.params):
                        raise exceptions.VisualizationError("bad operation record")

                    if op.condition:
                        raise exceptions.VisualizationError(
                            "If controlled measures currently not supported.")

                    if aliases:
                        newq = aliases[(qname, qindex)]
                        qname = newq[0]
                        qindex = newq[1]

                    pos_1 = self.img_regs[op.qargs[0]]
                    if self.cregbundle:
                        pos_2 = self.img_regs[self.clbit_list[0]]
                        cregindex = self.img_regs[op.cargs[0]] - pos_2
                        for creg_size in self.cregs.values():
                            if cregindex >= creg_size:
                                cregindex -= creg_size
                                pos_2 += 1
                            else:
                                break
                    else:
                        pos_2 = self.img_regs[op.cargs[0]]

                    try:
                        self._latex[pos_1][column] = "\\meter"
                        if self.cregbundle:
                            self._latex[pos_2][column] = \
                                "\\dstick{" + str(cregindex) + "} " + \
                                "\\cw \\cwx[-" + str(pos_2 - pos_1) + "]"
                        else:
                            self._latex[pos_2][column] = \
                                "\\cw \\cwx[-" + str(pos_2 - pos_1) + "]"
                    except Exception as e:
                        raise exceptions.VisualizationError(
                            'Error during Latex building: %s' % str(e))

                elif op.name in ['barrier', 'snapshot', 'load', 'save',
                                 'noise']:
                    if self.plot_barriers:
                        qarglist = op.qargs
                        indexes = [self._get_qubit_index(x) for x in qarglist]
                        indexes.sort()
                        if aliases is not None:
                            qarglist = map(lambda x: aliases[x], qarglist)

                        first = last = indexes[0]
                        for index in indexes[1:]:
                            if index - 1 == last:
                                last = index
                            else:
                                pos = self.img_regs[self.qubit_list[first]]
                                self._latex[pos][column - 1] += " \\barrier[0em]{" + str(
                                    last - first) + "}"
                                self._latex[pos][column] = "\\qw"
                                first = last = index
                        pos = self.img_regs[self.qubit_list[first]]
                        self._latex[pos][column - 1] += " \\barrier[0em]{" + str(
                            last - first) + "}"
                        self._latex[pos][column] = "\\qw"
                else:
                    raise exceptions.VisualizationError("bad node data")

            # increase the number of columns by the number of columns this layer used
            column += num_cols_used