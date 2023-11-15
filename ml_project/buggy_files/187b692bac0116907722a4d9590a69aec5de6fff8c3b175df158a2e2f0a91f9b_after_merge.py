def initialize_variables(variables=None, session=None, force=False, **run_kwargs):
    session = tf.get_default_session() if session is None else session
    if variables is None:
        initializer = tf.global_variables_initializer()
    else:
        if force:
            vars_for_init = list(_initializable_tensors(variables))
        else:
            vars_for_init = list(_find_initializable_tensors(variables, session))
        if not vars_for_init:
            return
        initializer = tf.variables_initializer(vars_for_init)
    session.run(initializer, **run_kwargs)