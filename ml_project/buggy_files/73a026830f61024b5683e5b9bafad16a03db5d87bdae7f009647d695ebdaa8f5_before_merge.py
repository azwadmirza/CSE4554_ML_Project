    def replacement_for_connection(self, connection, is_data=True):
        output_step_id = connection.output_step.id
        if output_step_id not in self.outputs:
            template = "No outputs found for step id %s, outputs are %s"
            message = template % (output_step_id, self.outputs)
            raise Exception(message)
        step_outputs = self.outputs[output_step_id]
        if step_outputs is STEP_OUTPUT_DELAYED:
            delayed_why = "dependent step [%s] delayed, so this step must be delayed" % output_step_id
            raise modules.DelayedWorkflowEvaluation(why=delayed_why)
        output_name = connection.output_name
        try:
            replacement = step_outputs[output_name]
        except KeyError:
            replacement = self.inputs_by_step_id.get(output_step_id)
            if connection.output_step.type == 'parameter_input' and output_step_id is not None:
                # FIXME: parameter_input step outputs should be properly recorded as step outputs, but for now we can
                # short-circuit and just pick the input value
                pass
            else:
                # Must resolve.
                template = "Workflow evaluation problem - failed to find output_name %s in step_outputs %s"
                message = template % (output_name, step_outputs)
                raise Exception(message)
        if isinstance(replacement, model.HistoryDatasetCollectionAssociation):
            if not replacement.collection.populated:
                if not replacement.collection.waiting_for_elements:
                    # If we are not waiting for elements, there was some
                    # problem creating the collection. Collection will never
                    # be populated.
                    # TODO: consider distinguish between cancelled and failed?
                    raise modules.CancelWorkflowEvaluation()

                delayed_why = "dependent collection [%s] not yet populated with datasets" % replacement.id
                raise modules.DelayedWorkflowEvaluation(why=delayed_why)

        data_inputs = (model.HistoryDatasetAssociation, model.HistoryDatasetCollectionAssociation, model.DatasetCollection)
        if not is_data and isinstance(replacement, data_inputs):
            if isinstance(replacement, model.HistoryDatasetAssociation):
                if replacement.is_pending:
                    raise modules.DelayedWorkflowEvaluation()
                if not replacement.is_ok:
                    raise modules.CancelWorkflowEvaluation()
            else:
                if not replacement.collection.populated:
                    raise modules.DelayedWorkflowEvaluation()
                pending = False
                for dataset_instance in replacement.dataset_instances:
                    if dataset_instance.is_pending:
                        pending = True
                    elif not dataset_instance.is_ok:
                        raise modules.CancelWorkflowEvaluation()
                if pending:
                    raise modules.DelayedWorkflowEvaluation()

        return replacement