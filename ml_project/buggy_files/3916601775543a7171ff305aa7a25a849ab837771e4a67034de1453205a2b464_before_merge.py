    def execute(self, image_obj, exec_context):
        """
        Execute the trigger specified in the rule with the image and gate (for prepared context) and exec_context)

        :param image_obj: The image to execute against
        :param exec_context: The prepared execution context from the gate init
        :return: a tuple of a list of errors and a list of PolicyRuleDecisions, one for each fired trigger match produced by the trigger execution
        """

        matches = None

        try:
            if not self.configured_trigger:
                log.error('No configured trigger to execute for gate {} and trigger: {}. Returning'.format(self.gate_name, self.trigger_name))
                raise TriggerNotFoundError(trigger_name=self.trigger_name, gate_name=self.gate_name)

            if self.gate_cls.__lifecycle_state__ == LifecycleStates.eol:
                self.errors.append(EndOfLifedError(gate_name=self.gate_name, superceded=self.gate_cls.__superceded_by__))
            elif self.gate_cls.__lifecycle_state__ == LifecycleStates.deprecated:
                self.errors.append(DeprecationWarning(gate_name=self.gate_name, superceded=self.gate_cls.__superceded_by__))
            elif self.configured_trigger.__lifecycle_state__ == LifecycleStates.eol:
                self.errors.append(EndOfLifedError(gate_name=self.gate_name, trigger_name=self.trigger_name, superceded=self.configured_trigger.__superceded_by__))
            elif self.configured_trigger.__lifecycle_state__ == LifecycleStates.deprecated:
                self.errors.append(DeprecationWarning(gate_name=self.gate_name, trigger_name=self.trigger_name, superceded=self.configured_trigger.__superceded_by__))

            try:
                self.configured_trigger.execute(image_obj, exec_context)
            except TriggerEvaluationError:
                raise
            except Exception as e:
                log.exception('Unmapped exception caught during trigger evaluation')
                raise TriggerEvaluationError(trigger=self.configured_trigger, message='Could not evaluate trigger due to error in evaluation execution')

            matches = self.configured_trigger.fired
            decisions = []

            # Try all rules and record all decisions and errors so multiple errors can be reported if present, not just the first encountered
            for match in matches:
                try:
                    decisions.append(PolicyRuleDecision(trigger_match=match, policy_rule=self))
                except TriggerEvaluationError as e:
                    log.exception('Policy rule decision mapping exception: {}'.format(e))
                    self.errors.append(str(e))

            return self.errors, decisions
        except Exception as e:
            log.exception('Error executing trigger {} on image {}'.format(self.trigger_name, image_obj.id))
            raise