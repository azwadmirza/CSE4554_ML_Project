    def get_data_outputs( self ):
        outputs = []
        if hasattr( self.subworkflow, 'workflow_outputs' ):
            for workflow_output in self.subworkflow.workflow_outputs:
                if workflow_output.workflow_step.type in {'data_input', 'data_collection_input'}:
                    # It is just confusing to display the input data as output data in subworkflows
                    continue
                output_step = workflow_output.workflow_step
                label = workflow_output.label
                if not label:
                    label = "%s:%s" % (output_step.order_index, workflow_output.output_name)
                output = dict(
                    name=label,
                    label=label,
                    extensions=['input'],  # TODO
                )
                outputs.append(output)
        return outputs