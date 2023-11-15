    def set_step_outputs(self, invocation_step, outputs, already_persisted=False):
        step = invocation_step.workflow_step
        if invocation_step.output_value:
            outputs[invocation_step.output_value.workflow_output.output_name] = invocation_step.output_value.value
        self.outputs[step.id] = outputs
        if not already_persisted:
            for workflow_output in step.workflow_outputs:
                output_name = workflow_output.output_name
                if output_name not in outputs:
                    message = "Failed to find expected workflow output [{}] in step outputs [{}]".format(output_name, outputs)
                    # raise KeyError(message)
                    # Pre-18.01 we would have never even detected this output wasn't configured
                    # and even in 18.01 we don't have a way to tell the user something bad is
                    # happening so I guess we just log a debug message and continue sadly for now.
                    # Once https://github.com/galaxyproject/galaxy/issues/5142 is complete we could
                    # at least tell the user what happened, give them a warning.
                    log.debug(message)
                    continue
                output = outputs[output_name]
                self._record_workflow_output(
                    step,
                    workflow_output,
                    output=output,
                )