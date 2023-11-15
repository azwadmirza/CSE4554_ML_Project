    def add_output(self, workflow_output, step, output_object):
        if step.type == 'parameter_input':
            # TODO: these should be properly tracked.
            return
        if output_object.history_content_type == "dataset":
            output_assoc = WorkflowInvocationOutputDatasetAssociation()
            output_assoc.workflow_invocation = self
            output_assoc.workflow_output = workflow_output
            output_assoc.workflow_step = step
            output_assoc.dataset = output_object
            self.output_datasets.append(output_assoc)
        elif output_object.history_content_type == "dataset_collection":
            output_assoc = WorkflowInvocationOutputDatasetCollectionAssociation()
            output_assoc.workflow_invocation = self
            output_assoc.workflow_output = workflow_output
            output_assoc.workflow_step = step
            output_assoc.dataset_collection = output_object
            self.output_dataset_collections.append(output_assoc)
        else:
            raise Exception("Unknown output type encountered")