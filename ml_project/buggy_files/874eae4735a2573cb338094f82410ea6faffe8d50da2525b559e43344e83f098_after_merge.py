    def get_data_inputs( self ):
        """ Get configure time data input descriptions. """
        # Filter subworkflow steps and get inputs
        step_to_input_type = {
            "data_input": "dataset",
            "data_collection_input": "dataset_collection",
        }
        inputs = []
        if hasattr( self.subworkflow, 'input_steps' ):
            for step in self.subworkflow.input_steps:
                name = step.label
                if not name:
                    step_module = module_factory.from_workflow_step( self.trans, step )
                    name = "%s:%s" % (step.order_index, step_module.get_name())
                step_type = step.type
                assert step_type in step_to_input_type
                input = dict(
                    input_subworkflow_step_id=step.order_index,
                    name=name,
                    label=name,
                    multiple=False,
                    extensions="input",
                    input_type=step_to_input_type[step_type],
                )
                inputs.append(input)
        return inputs