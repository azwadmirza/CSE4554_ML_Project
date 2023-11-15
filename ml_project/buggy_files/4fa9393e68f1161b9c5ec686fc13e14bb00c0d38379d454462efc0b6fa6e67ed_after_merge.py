    def execute( self, trans, progress, invocation, step ):
        """ Execute the given workflow step in the given workflow invocation.
        Use the supplied workflow progress object to track outputs, find
        inputs, etc...
        """
        subworkflow_invoker = progress.subworkflow_invoker( trans, step )
        subworkflow_invoker.invoke()
        subworkflow = subworkflow_invoker.workflow
        subworkflow_progress = subworkflow_invoker.progress
        outputs = {}
        for workflow_output in subworkflow.workflow_outputs:
            workflow_output_label = workflow_output.label or "%s:%s" % (step.order_index, workflow_output.output_name)
            replacement = subworkflow_progress.get_replacement_workflow_output( workflow_output )
            outputs[ workflow_output_label ] = replacement
        progress.set_step_outputs( step, outputs )
        return None