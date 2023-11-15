    def autoflow_wrapper(method):
        @functools.wraps(method)
        def runnable(obj, *args, **kwargs):
            if not isinstance(obj, Node):
                raise GPflowError(
                    'AutoFlow works only with node-like objects.')
            if obj.is_built_coherence(obj.graph) is Build.NO:
                raise GPflowError('Not built with "{graph}".'.format(graph=obj.graph))
            name = method.__name__
            store = AutoFlow.get_autoflow(obj, name)
            session = kwargs.pop('session', None)
            session = obj.enquire_session(session=session)

            scope_name = _name_scope_name(obj, name)
            with session.graph.as_default(), tf.name_scope(scope_name):
                if not store:
                    _setup_storage(store, *af_args, **af_kwargs)
                    _build_method(method, obj, store)
                return _session_run(session, obj, store, *args, **kwargs)
        return runnable