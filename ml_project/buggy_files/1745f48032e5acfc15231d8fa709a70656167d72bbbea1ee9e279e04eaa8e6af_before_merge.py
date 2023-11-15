    def __init__(self, parent_gate_cls, rule_id=None, **kwargs):
        """
        Instantiate the trigger with a specific set of parameters. Does not evaluate the trigger, just configures
        it for execution.
        """
        self.gate_cls = parent_gate_cls
        self.msg = None
        self.eval_params = {}
        self._fired_instances = []
        self.rule_id = rule_id

        # Short circuit if gate is eol or trigger is eol
        if self.gate_cls.__lifecycle_state__ == LifecycleStates.eol or self.__lifecycle_state__ == LifecycleStates.eol:
            return

        # Setup the parameters, try setting each. If not provided, set to None to handle validation path for required params
        invalid_params = []

        # The list of class vars that are parameters
        params = self.__class__._parameters()

        param_name_map = {}

        if kwargs is None:
            kwargs = {}

        # Find all class objects that are params
        for attr_name, param_obj in list(params.items()):
            for a in param_obj.aliases:
                param_name_map[a] = param_obj.name

            param_name_map[param_obj.name] = param_obj.name

            try:
                setattr(self, attr_name, copy.deepcopy(param_obj))
                param_value = kwargs.get(param_obj.name, None)
                if param_value is None:
                    # Try aliases
                    for alias in param_obj.aliases:
                        param_value = kwargs.get(alias, None)
                        if param_value:
                            break

                getattr(self, attr_name).set_value(param_value)
            except ValidationError as e:
                invalid_params.append(ParameterValueInvalidError(validation_error=e, gate=self.gate_cls.__gate_name__, trigger=self.__trigger_name__, rule_id=self.rule_id))

        # Then, check for any parameters provided that are not defined in the trigger.
        if kwargs:
            given_param_names = set([param_name_map.get(x) for x in list(kwargs.keys())])
            for i in given_param_names.difference(set([x.name for x in list(params.values())])):
                # Need to aggregate and return all invalid if there is more than one
                invalid_params.append(InvalidParameterError(i, list(params.keys()), trigger=self.__trigger_name__, gate=self.gate_cls.__gate_name__))

        if invalid_params:
            raise PolicyRuleValidationErrorCollection(invalid_params, trigger=self.__trigger_name__, gate=self.gate_cls.__gate_name__)