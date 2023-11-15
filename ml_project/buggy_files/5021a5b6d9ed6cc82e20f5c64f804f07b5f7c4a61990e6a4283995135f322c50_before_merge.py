    def body_fn(val):
        i, loss, opt_state_, rng_ = val
        loss, opt_state_, rng_ = svi_update(i, rng_, opt_state_)
        return i + 1, loss, opt_state_, rng_