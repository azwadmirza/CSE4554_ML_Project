    def save_resume_data(self):
        """
        method to save resume data.
        """
        # only call libtorrent save resume in the first call
        if not self.deferreds_resume:
            self.handle.save_resume_data()

        defer_resume = Deferred()
        defer_resume.addErrback(self._on_resume_err)

        self.deferreds_resume.append(defer_resume)

        return defer_resume