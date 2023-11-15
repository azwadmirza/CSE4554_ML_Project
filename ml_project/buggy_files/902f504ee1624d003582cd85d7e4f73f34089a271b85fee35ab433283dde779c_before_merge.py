    def _on_show_prompts(self, question):
        """Show a prompt for the given question.

        Args:
            question: A Question object or None.
        """
        item = self._layout.takeAt(0)
        if item is not None:
            widget = item.widget()
            log.prompt.debug("Deleting old prompt {}".format(widget))
            widget.hide()
            widget.deleteLater()

        if question is None:
            log.prompt.debug("No prompts left, hiding prompt container.")
            self._prompt = None
            self.hide()
            return

        classes = {
            usertypes.PromptMode.yesno: YesNoPrompt,
            usertypes.PromptMode.text: LineEditPrompt,
            usertypes.PromptMode.user_pwd: AuthenticationPrompt,
            usertypes.PromptMode.download: DownloadFilenamePrompt,
            usertypes.PromptMode.alert: AlertPrompt,
        }
        klass = classes[question.mode]
        prompt = klass(question)

        log.prompt.debug("Displaying prompt {}".format(prompt))
        self._prompt = prompt

        if not question.interrupted:
            # If this question was interrupted, we already connected the signal
            question.aborted.connect(
                lambda: modeman.leave(self._win_id, prompt.KEY_MODE, 'aborted',
                                      maybe=True))
        modeman.enter(self._win_id, prompt.KEY_MODE, 'question asked')

        self.setSizePolicy(prompt.sizePolicy())
        self._layout.addWidget(prompt)
        prompt.show()
        self.show()
        prompt.setFocus()
        self.update_geometry.emit()