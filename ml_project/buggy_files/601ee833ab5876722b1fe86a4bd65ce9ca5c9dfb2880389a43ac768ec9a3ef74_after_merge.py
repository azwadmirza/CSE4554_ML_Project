    def top_level_workflow(self):
        """ If this workflow is not attached to stored workflow directly,
        recursively grab its parents until it is the top level workflow
        which must have a stored workflow associated with it.
        """
        top_level_workflow = self
        if self.stored_workflow is None:
            # TODO: enforce this at creation...
            assert len(set(w.uuid for w in self.parent_workflow_steps)) == 1
            return self.parent_workflow_steps[0].workflow.top_level_workflow
        return top_level_workflow