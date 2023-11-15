    def save_resume_data(self):
        """
        Save the resume data of a download. This method returns a deferred that fires when the resume data is available.
        Note that this method only calls save_resume_data once on subsequent calls.
        """
        if not self.deferreds_resume:
            self.get_handle().addCallback(lambda handle: handle.save_resume_data())

        defer_resume = Deferred()
        defer_resume.addErrback(self._on_resume_err)

        self.deferreds_resume.append(defer_resume)

        return defer_resume