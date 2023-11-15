    def handle(cls, op, results, mock=False):
        method_name, mapper = ('execute', cls._op_runners) if not mock else \
            ('estimate_size', cls._op_size_estimators)
        try:
            runner = mapper[type(op)]
        except KeyError:
            runner = getattr(op, method_name)

        # register a custom serializer for Mars operand
        _register_ray_serializer(op)

        try:
            ray.wait([execute_on_ray.remote(runner, results, op)])
        except NotImplementedError:
            for op_cls in mapper.keys():
                if isinstance(op, op_cls):
                    mapper[type(op)] = mapper[op_cls]
                    runner = mapper[op_cls]

                    ray.wait(
                        [execute_on_ray.remote(runner, results, op)])
            raise KeyError(f'No handler found for op: {op}')