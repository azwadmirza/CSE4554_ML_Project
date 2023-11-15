        def body_fn(i, val):
            loss_sum, opt_state, rng = val
            rng, rng_binarize = random.split(rng)
            batch = binarize(rng_binarize, train_fetch(i, train_idx)[0])
            # TODO: we will want to merge (i, rng, opt_state) into `svi_state`
            # Here the index `i` is reseted after each epoch, which causes no
            # problem for static learning rate, but it is not a right way for
            # scheduled learning rate.
            loss, opt_state, rng = svi_update(i, rng, opt_state, (batch,), (batch,),)
            loss_sum += loss
            return loss_sum, opt_state, rng