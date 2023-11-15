    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa C901
        fields: Dict[str, ModelField] = {}
        config = BaseConfig
        validators: 'ValidatorListDict' = {}
        fields_defaults: Dict[str, Any] = {}

        pre_root_validators, post_root_validators = [], []
        for base in reversed(bases):
            if _is_base_model_class_defined and issubclass(base, BaseModel) and base != BaseModel:
                fields.update(deepcopy(base.__fields__))
                config = inherit_config(base.__config__, config)
                validators = inherit_validators(base.__validators__, validators)
                pre_root_validators += base.__pre_root_validators__
                post_root_validators += base.__post_root_validators__

        config = inherit_config(namespace.get('Config'), config)
        validators = inherit_validators(extract_validators(namespace), validators)
        vg = ValidatorGroup(validators)

        for f in fields.values():
            if not f.required:
                fields_defaults[f.name] = f.default

            f.set_config(config)
            extra_validators = vg.get_validators(f.name)
            if extra_validators:
                f.class_validators.update(extra_validators)
                # re-run prepare to add extra validators
                f.populate_validators()

        prepare_config(config, name)

        class_vars = set()
        if (namespace.get('__module__'), namespace.get('__qualname__')) != ('pydantic.main', 'BaseModel'):
            annotations = resolve_annotations(namespace.get('__annotations__', {}), namespace.get('__module__', None))
            untouched_types = UNTOUCHED_TYPES + config.keep_untouched
            # annotation only fields need to come first in fields
            for ann_name, ann_type in annotations.items():
                if is_classvar(ann_type):
                    class_vars.add(ann_name)
                elif is_valid_field(ann_name):
                    validate_field_name(bases, ann_name)
                    value = namespace.get(ann_name, Undefined)
                    if (
                        isinstance(value, untouched_types)
                        and ann_type != PyObject
                        and not lenient_issubclass(getattr(ann_type, '__origin__', None), Type)
                    ):
                        continue
                    fields[ann_name] = inferred = ModelField.infer(
                        name=ann_name,
                        value=value,
                        annotation=ann_type,
                        class_validators=vg.get_validators(ann_name),
                        config=config,
                    )
                    if not inferred.required:
                        fields_defaults[ann_name] = inferred.default

            for var_name, value in namespace.items():
                if (
                    var_name not in annotations
                    and is_valid_field(var_name)
                    and not isinstance(value, untouched_types)
                    and var_name not in class_vars
                ):
                    validate_field_name(bases, var_name)
                    inferred = ModelField.infer(
                        name=var_name,
                        value=value,
                        annotation=annotations.get(var_name),
                        class_validators=vg.get_validators(var_name),
                        config=config,
                    )
                    if var_name in fields and inferred.type_ != fields[var_name].type_:
                        raise TypeError(
                            f'The type of {name}.{var_name} differs from the new default value; '
                            f'if you wish to change the type of this field, please use a type annotation'
                        )
                    fields[var_name] = inferred
                    if not inferred.required:
                        fields_defaults[var_name] = inferred.default

        _custom_root_type = ROOT_KEY in fields
        if _custom_root_type:
            validate_custom_root_type(fields)
        vg.check_for_unused()
        if config.json_encoders:
            json_encoder = partial(custom_pydantic_encoder, config.json_encoders)
        else:
            json_encoder = pydantic_encoder
        pre_rv_new, post_rv_new = extract_root_validators(namespace)
        new_namespace = {
            '__config__': config,
            '__fields__': fields,
            '__field_defaults__': fields_defaults,
            '__validators__': vg.validators,
            '__pre_root_validators__': pre_root_validators + pre_rv_new,
            '__post_root_validators__': post_root_validators + post_rv_new,
            '__schema_cache__': {},
            '__json_encoder__': staticmethod(json_encoder),
            '__custom_root_type__': _custom_root_type,
            **{n: v for n, v in namespace.items() if n not in fields},
        }

        cls = super().__new__(mcs, name, bases, new_namespace, **kwargs)
        # set __signature__ attr only for model class, but not for its instances
        cls.__signature__ = ClassAttribute('__signature__', generate_model_signature(cls.__init__, fields, config))
        return cls