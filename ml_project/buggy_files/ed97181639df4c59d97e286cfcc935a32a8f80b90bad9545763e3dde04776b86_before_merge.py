    def _serialize(cls, var: Any) -> Any:  # Unfortunately there is no support for recursive types in mypy
        """Helper function of depth first search for serialization.

        The serialization protocol is:

        (1) keeping JSON supported types: primitives, dict, list;
        (2) encoding other types as ``{TYPE: 'foo', VAR: 'bar'}``, the deserialization
            step decode VAR according to TYPE;
        (3) Operator has a special field CLASS to record the original class
            name for displaying in UI.
        """
        try:
            if cls._is_primitive(var):
                # enum.IntEnum is an int instance, it causes json dumps error so we use its value.
                if isinstance(var, enum.Enum):
                    return var.value
                return var
            elif isinstance(var, dict):
                return cls._encode(
                    {str(k): cls._serialize(v) for k, v in var.items()},
                    type_=DAT.DICT
                )
            elif isinstance(var, k8s.V1Pod):
                json_pod = PodGenerator.serialize_pod(var)
                return cls._encode(json_pod, type_=DAT.POD)
            elif isinstance(var, list):
                return [cls._serialize(v) for v in var]
            elif isinstance(var, k8s.V1Pod):
                json_pod = PodGenerator.serialize_pod(var)
                return cls._encode(json_pod, type_=DAT.POD)
            elif isinstance(var, DAG):
                return SerializedDAG.serialize_dag(var)
            elif isinstance(var, BaseOperator):
                return SerializedBaseOperator.serialize_operator(var)
            elif isinstance(var, cls._datetime_types):
                return cls._encode(var.timestamp(), type_=DAT.DATETIME)
            elif isinstance(var, datetime.timedelta):
                return cls._encode(var.total_seconds(), type_=DAT.TIMEDELTA)
            elif isinstance(var, Timezone):
                return cls._encode(str(var.name), type_=DAT.TIMEZONE)
            elif isinstance(var, relativedelta.relativedelta):
                encoded = {k: v for k, v in var.__dict__.items() if not k.startswith("_") and v}
                if var.weekday and var.weekday.n:
                    # Every n'th Friday for example
                    encoded['weekday'] = [var.weekday.weekday, var.weekday.n]
                elif var.weekday:
                    encoded['weekday'] = [var.weekday.weekday]
                return cls._encode(encoded, type_=DAT.RELATIVEDELTA)
            elif callable(var):
                return str(get_python_source(var))
            elif isinstance(var, set):
                # FIXME: casts set to list in customized serialization in future.
                return cls._encode(
                    [cls._serialize(v) for v in var], type_=DAT.SET)
            elif isinstance(var, tuple):
                # FIXME: casts tuple to list in customized serialization in future.
                return cls._encode(
                    [cls._serialize(v) for v in var], type_=DAT.TUPLE)
            elif isinstance(var, TaskGroup):
                return SerializedTaskGroup.serialize_task_group(var)
            else:
                log.debug('Cast type %s to str in serialization.', type(var))
                return str(var)
        except Exception:  # pylint: disable=broad-except
            log.error('Failed to stringify.', exc_info=True)
            return FAILED