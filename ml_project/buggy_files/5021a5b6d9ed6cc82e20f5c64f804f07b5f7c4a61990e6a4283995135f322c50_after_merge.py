    def body_fn(val, i):
        opt_state_, rng_ = val
        loss, opt_state_, rng_ = svi_update(i, rng_, opt_state_)
        return (opt_state_, rng_), loss