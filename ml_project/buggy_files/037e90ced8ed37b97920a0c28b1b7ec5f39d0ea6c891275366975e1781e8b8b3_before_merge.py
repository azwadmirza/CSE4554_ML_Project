    def _append_pserver_ops(self, optimize_block, opt_op, endpoint):
        program = optimize_block.program
        pserver_block = program.global_block()
        new_inputs = dict()
        # update param/grad shape first, then other inputs like
        # moment can use the updated shape
        for key in opt_op.input_names:
            if key == "Grad":
                grad_block = None
                for g in self.param_grad_ep_mapping[endpoint]["grads"]:
                    if same_or_split_var(
                            self._orig_varname(g.name), opt_op.input(key)[0]):
                        grad_block = g
                        break
                if not grad_block:
                    # do not append this op if current endpoint
                    # is not dealing with this grad block
                    return
                merged_var = \
                    pserver_block.vars[self._orig_varname(grad_block.name)]
                if self.trainers > 1:
                    vars2merge = []
                    for i in xrange(self.trainers):
                        per_trainer_name = "%s.trainer_%d" % \
                        (self._orig_varname(grad_block.name), i)
                        vars2merge.append(pserver_block.vars[per_trainer_name])

                    optimize_block.append_op(
                        type="sum",
                        inputs={"X": vars2merge},
                        outputs={"Out": merged_var})
                    if not merged_var.type == core.VarDesc.VarType.SELECTED_ROWS:
                        optimize_block.append_op(
                            type="scale",
                            inputs={"X": merged_var},
                            outputs={"Out": merged_var},
                            attrs={"scale": 1.0 / float(self.trainers)})
                new_inputs[key] = merged_var
            elif key == "Param":
                # param is already created on global program
                param_block = None
                for p in self.param_grad_ep_mapping[endpoint]["params"]:
                    if same_or_split_var(p.name, opt_op.input(key)[0]):
                        param_block = p
                        break
                if not param_block:
                    return
                tmpvar = pserver_block.create_var(
                    name=param_block.name,
                    persistable=True,
                    dtype=param_block.dtype,
                    shape=param_block.shape)
                new_inputs[key] = tmpvar
            elif key == "LearningRate":
                # leraning rate variable has already be created by non-optimize op,
                # don't create it once again.
                new_inputs[key] = pserver_block.vars[opt_op.input(key)[0]]

        for key in opt_op.input_names:
            new_shape = None
            if key in ["Param", "Grad", "LearningRate"]:
                continue
            var = self.program.global_block().vars[opt_op.input(key)[0]]
            # update accumulator variable shape
            param_shape = new_inputs["Param"].shape
            new_shape = self._get_optimizer_input_shape(opt_op.type, key,
                                                        var.shape, param_shape)
            tmpvar = pserver_block.create_var(
                name=var.name,
                persistable=var.persistable,
                dtype=var.dtype,
                shape=new_shape)
            new_inputs[key] = tmpvar

        # change output's ParamOut variable
        outputs = self._get_output_map_from_op(self.program.global_block().vars,
                                               opt_op)
        outputs["ParamOut"] = new_inputs["Param"]

        optimize_block.append_op(
            type=opt_op.type,
            inputs=new_inputs,
            outputs=outputs,
            attrs=opt_op.attrs)