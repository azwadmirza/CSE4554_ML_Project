    def get_pserver_program(self, endpoint):
        """
        Get pserver side program using the endpoint.
        NOTE: assume blocks of the same variable is not distributed
        on the same pserver, only change param/grad varnames for
        trainers to fetch.
        """
        # step1
        pserver_program = Program()
        # step2
        recv_inputs = []
        for v in self.param_grad_ep_mapping[endpoint]["params"]:
            self._clone_var(pserver_program.global_block(), v)
        for v in self.param_grad_ep_mapping[endpoint]["grads"]:
            # create vars for each trainer in global scope, so
            # we don't need to create them when grad arrives.
            # change client side var name to origin name by
            # removing ".trainer_%d" suffix
            suff_idx = v.name.find(".trainer_")
            if suff_idx >= 0:
                orig_var_name = v.name[:suff_idx]
            pserver_program.global_block().create_var(
                name=orig_var_name,
                persistable=True,
                type=v.type,
                dtype=v.dtype,
                shape=v.shape)
            for trainer_id in xrange(self.trainers):
                var = pserver_program.global_block().create_var(
                    name="%s.trainer_%d" % (orig_var_name, trainer_id),
                    persistable=False,
                    type=v.type,
                    dtype=v.dtype,
                    shape=v.shape)
                recv_inputs.append(var)
        # step3
        optimize_block = pserver_program.create_block(0)
        # step 4
        # Create a union-find data struct from optimize ops,
        # If two ops are connected, we could add these two ops
        # into one set.
        ufind = self._create_ufind(self.optimize_ops)
        # step 4.2 
        # Iterate through the ops and append optimize op which
        # located on current pserver
        opt_op_on_pserver = []
        for _, op in enumerate(self.optimize_ops):
            if self._is_opt_op(op) and self._is_opt_op_on_pserver(endpoint, op):
                opt_op_on_pserver.append(op)
        # step 4.3
        # Iterate through the ops, and if an op and the optimize ops
        # which located on current pserver are in one set, then 
        # append it into the sub program.
        for _, op in enumerate(self.optimize_ops):
            for _, opt_op in enumerate(opt_op_on_pserver):
                if ufind.is_connected(op, opt_op):
                    if self._is_opt_op(op):
                        self._append_pserver_ops(optimize_block, op, endpoint)
                    else:
                        self._append_pserver_non_opt_ops(optimize_block, op)
                    break
        # step5 append the listen_and_serv op
        pserver_program.global_block().append_op(
            type="listen_and_serv",
            inputs={'X': recv_inputs},
            outputs={},
            attrs={
                "OptimizeBlock": optimize_block,
                "endpoint": endpoint,
                "Fanin": self.trainers
            })
        pserver_program.sync_with_cpp()
        return pserver_program