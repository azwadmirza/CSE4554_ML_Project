    def setup(self, action: int, checksum: bytes, app_id: bytes) -> bool:
        if workflow.tasks or self.workflow:
            # If any other workflow is running, we bail out.
            return False

        self.action = action
        self.checksum = checksum
        self.app_id = app_id

        self.confirmed = None
        self.workflow = self.confirm_workflow()
        loop.schedule(self.workflow)
        return True