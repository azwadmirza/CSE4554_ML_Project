def rl_on_new_line():
    """Grabs one of a few possible redisplay functions in readline."""
    names = ['rl_on_new_line', 'rl_forced_update_display', 'rl_redisplay']
    for name in names:
        func = getattr(RL_LIB, name, None)
        if func is not None:
            break
    return func