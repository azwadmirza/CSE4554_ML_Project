    def __init__(self, parent, policy_json=None):
        super(ExecutablePolicyRule, self).__init__(parent, policy_json)

        # Configure the trigger instance
        try:
            self.gate_cls = Gate.get_gate_by_name(self.gate_name)
        except KeyError:
            # Gate not found
            self.error_exc = GateNotFoundError(gate=self.gate_name, valid_gates=Gate.registered_gate_names(), rule_id=self.rule_id)
            self.configured_trigger = None
            raise self.error_exc

        try:
            selected_trigger_cls = self.gate_cls.get_trigger_named(self.trigger_name.lower())
        except KeyError:
            self.error_exc = TriggerNotFoundError(valid_triggers=self.gate_cls.trigger_names(), trigger=self.trigger_name, gate=self.gate_name, rule_id=self.rule_id)
            self.configured_trigger = None
            raise self.error_exc

        try:
            try:
                self.configured_trigger = selected_trigger_cls(parent_gate_cls=self.gate_cls, rule_id=self.rule_id, **self.trigger_params)
            except (TriggerNotFoundError, InvalidParameterError, ParameterValueInvalidError) as e:
                # Error finding or initializing the trigger
                self.error_exc = e
                self.configured_trigger = None

                if hasattr(e, 'gate') and e.gate is None:
                    e.gate = self.gate_name
                if hasattr(e, 'trigger') and e.trigger is None:
                    e.trigger = self.trigger_name
                if hasattr(e, 'rule_id') and e.rule_id is None:
                    e.rule_id = self.rule_id
                raise e
        except PolicyError:
            raise # To filter out already-handled errors
        except Exception as e:
            raise ValidationError.caused_by(e)