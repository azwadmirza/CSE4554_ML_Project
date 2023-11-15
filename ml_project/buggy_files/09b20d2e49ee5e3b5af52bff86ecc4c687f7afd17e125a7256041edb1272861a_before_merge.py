    def create(self, name_or_url, **kwargs):
        # create url.URL object
        u = url.make_url(name_or_url)

        plugins = u._instantiate_plugins(kwargs)

        u.query.pop("plugin", None)
        kwargs.pop("plugins", None)

        entrypoint = u._get_entrypoint()
        dialect_cls = entrypoint.get_dialect_cls(u)

        if kwargs.pop("_coerce_config", False):

            def pop_kwarg(key, default=None):
                value = kwargs.pop(key, default)
                if key in dialect_cls.engine_config_types:
                    value = dialect_cls.engine_config_types[key](value)
                return value

        else:
            pop_kwarg = kwargs.pop

        dialect_args = {}
        # consume dialect arguments from kwargs
        for k in util.get_cls_kwargs(dialect_cls):
            if k in kwargs:
                dialect_args[k] = pop_kwarg(k)

        dbapi = kwargs.pop("module", None)
        if dbapi is None:
            dbapi_args = {}
            for k in util.get_func_kwargs(dialect_cls.dbapi):
                if k in kwargs:
                    dbapi_args[k] = pop_kwarg(k)
            dbapi = dialect_cls.dbapi(**dbapi_args)

        dialect_args["dbapi"] = dbapi

        for plugin in plugins:
            plugin.handle_dialect_kwargs(dialect_cls, dialect_args)

        # create dialect
        dialect = dialect_cls(**dialect_args)

        # assemble connection arguments
        (cargs, cparams) = dialect.create_connect_args(u)
        cparams.update(pop_kwarg("connect_args", {}))
        cargs = list(cargs)  # allow mutability

        # look for existing pool or create
        pool = pop_kwarg("pool", None)
        if pool is None:

            def connect(connection_record=None):
                if dialect._has_events:
                    for fn in dialect.dispatch.do_connect:
                        connection = fn(
                            dialect, connection_record, cargs, cparams
                        )
                        if connection is not None:
                            return connection
                return dialect.connect(*cargs, **cparams)

            creator = pop_kwarg("creator", connect)

            poolclass = pop_kwarg("poolclass", None)
            if poolclass is None:
                poolclass = dialect_cls.get_pool_class(u)
            pool_args = {"dialect": dialect}

            # consume pool arguments from kwargs, translating a few of
            # the arguments
            translate = {
                "logging_name": "pool_logging_name",
                "echo": "echo_pool",
                "timeout": "pool_timeout",
                "recycle": "pool_recycle",
                "events": "pool_events",
                "use_threadlocal": "pool_threadlocal",
                "reset_on_return": "pool_reset_on_return",
                "pre_ping": "pool_pre_ping",
                "use_lifo": "pool_use_lifo",
            }
            for k in util.get_cls_kwargs(poolclass):
                tk = translate.get(k, k)
                if tk in kwargs:
                    pool_args[k] = pop_kwarg(tk)

            for plugin in plugins:
                plugin.handle_pool_kwargs(poolclass, pool_args)

            pool = poolclass(creator, **pool_args)
        else:
            if isinstance(pool, poollib.dbapi_proxy._DBProxy):
                pool = pool.get_pool(*cargs, **cparams)
            else:
                pool = pool

            pool._dialect = dialect

        # create engine.
        engineclass = self.engine_cls
        engine_args = {}
        for k in util.get_cls_kwargs(engineclass):
            if k in kwargs:
                engine_args[k] = pop_kwarg(k)

        _initialize = kwargs.pop("_initialize", True)

        # all kwargs should be consumed
        if kwargs:
            raise TypeError(
                "Invalid argument(s) %s sent to create_engine(), "
                "using configuration %s/%s/%s.  Please check that the "
                "keyword arguments are appropriate for this combination "
                "of components."
                % (
                    ",".join("'%s'" % k for k in kwargs),
                    dialect.__class__.__name__,
                    pool.__class__.__name__,
                    engineclass.__name__,
                )
            )

        engine = engineclass(pool, dialect, u, **engine_args)

        if _initialize:
            do_on_connect = dialect.on_connect()
            if do_on_connect:

                def on_connect(dbapi_connection, connection_record):
                    conn = getattr(
                        dbapi_connection, "_sqla_unwrap", dbapi_connection
                    )
                    if conn is None:
                        return
                    do_on_connect(conn)

                event.listen(pool, "first_connect", on_connect)
                event.listen(pool, "connect", on_connect)

            def first_connect(dbapi_connection, connection_record):
                c = base.Connection(
                    engine, connection=dbapi_connection, _has_events=False
                )
                c._execution_options = util.immutabledict()
                dialect.initialize(c)
                dialect.do_rollback(c.connection)

            event.listen(pool, "first_connect", first_connect, once=True)

        dialect_cls.engine_created(engine)
        if entrypoint is not dialect_cls:
            entrypoint.engine_created(engine)

        for plugin in plugins:
            plugin.engine_created(engine)

        return engine