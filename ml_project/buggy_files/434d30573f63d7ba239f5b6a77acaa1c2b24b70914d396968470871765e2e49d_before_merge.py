    def epoch_train(opt_state, rng):
        def body_fn(i, val):
            loss_sum, opt_state, rng = val
            rng, rng_binarize = random.split(rng)
            batch = binarize(rng_binarize, train_fetch(i, train_idx)[0])
            loss, opt_state, rng = svi_update(i, rng, opt_state, (batch,), (batch,),)
            loss_sum += loss
            return loss_sum, opt_state, rng

        return lax.fori_loop(0, num_train, body_fn, (0., opt_state, rng))