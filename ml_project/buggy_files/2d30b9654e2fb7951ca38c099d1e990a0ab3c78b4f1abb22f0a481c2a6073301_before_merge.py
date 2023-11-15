    def handle(cls, op, results, mock=False):
        method_name, mapper = ('execute', cls._op_runners) if not mock else \
            ('estimate_size', cls._op_size_estimators)
        try:
            runner = mapper[type(op)]
        except KeyError:
            runner = getattr(op, method_name)

        # register a custom serializer for Mars operand
        _register_ray_serializer(op)

        @lru_cache(500)
        def build_remote_funtion(func):

            @ray.remote
            def remote_runner(results, op):
                return func(results, op)

            return remote_runner

        try:
            return ray.get(build_remote_funtion(runner).remote(results, op))
        except NotImplementedError:
            for op_cls in mapper.keys():
                if isinstance(op, op_cls):
                    mapper[type(op)] = mapper[op_cls]
                    runner = mapper[op_cls]

                    return ray.get(
                        build_remote_funtion(runner).remote(results, op))
            raise KeyError(f'No handler found for op: {op}')