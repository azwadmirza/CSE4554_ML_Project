def while_loop(cond_fun, body_fun, init_val):
    if _DISABLE_CONTROL_FLOW_PRIM:
        val = init_val
        while cond_fun(val):
            val = body_fun(val)
        return val
    else:
        # TODO: consider jitting while_loop similar to fori_loop
        return lax.while_loop(cond_fun, body_fun, init_val)