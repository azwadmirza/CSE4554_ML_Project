def initialize_variables(variables=None, session=None, force=False, **run_kwargs):
    session = tf.get_default_session() if session is None else session
    if variables is None:
        initializer = tf.global_variables_initializer()
    else:
        if force:
            initializer = tf.variables_initializer(variables)
        else:
            uninitialized = tf.report_uninitialized_variables(var_list=variables)
            def uninitialized_names():
                for uv in session.run(uninitialized):
                    yield uv.decode('utf-8')
                    # if isinstance(uv, bytes):
                    #     yield uv.decode('utf-8')
                    # elif isinstance(uv, str):
                    #     yield uv
                    # else:
                    #     msg = 'Unknown output type "{}" from `tf.report_uninitialized_variables`'
                    #     raise ValueError(msg.format(type(uv)))
            names = set(uninitialized_names())
            vars_for_init = [v for v in variables if v.name.split(':')[0] in names]
            initializer = tf.variables_initializer(vars_for_init)
    session.run(initializer, **run_kwargs)