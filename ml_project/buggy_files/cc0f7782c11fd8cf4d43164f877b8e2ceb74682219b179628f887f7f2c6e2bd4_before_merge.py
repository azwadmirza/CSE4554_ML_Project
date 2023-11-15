    def __init__(
        self,
        *,
        name: str,
        type_: Type,
        class_validators: List[Validator],
        default: Any,
        required: bool,
        model_config: Any,
        alias: str = None,
        allow_none: bool = False,
        schema: Schema = None,
    ):

        self.name: str = name
        self.alias: str = alias or name
        self.type_: type = type_
        self.class_validators = class_validators or []
        self.validate_always: bool = False
        self.sub_fields: List[Field] = None
        self.key_field: Field = None
        self.validators = []
        self.whole_pre_validators = None
        self.whole_post_validators = None
        self.default: Any = default
        self.required: bool = required
        self.model_config = model_config
        self.allow_none: bool = allow_none
        self.parse_json: bool = False
        self.shape: Shape = Shape.SINGLETON
        self._schema: Schema = schema
        self.prepare()