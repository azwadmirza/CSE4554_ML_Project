    def set_text(self, text, transaction_ids=[]):
        """
        deletes all the old notes in a task and sets a single note with the
        given text
        """
        # delete old notes
        notes = self.rtm_taskseries.notes
        if notes:
            note_list = self.__getattr_the_rtm_way(notes, 'note')
            for note_id in [note.id for note in note_list]:
                result = self.rtm.tasksNotes.delete(timeline=self.timeline,
                                                    note_id=note_id)
                transaction_ids.append(result.transaction.id)

        if text == "":
            return
        text = html.escape(text)

        # RTM does not support well long notes (that is, it denies the request)
        # Thus, we split long text in chunks. To make them show in the correct
        # order on the website, we have to upload them from the last to the
        # first (they show the most recent on top)
        text_cursor_end = len(text)
        while True:
            text_cursor_start = text_cursor_end - 1000
            if text_cursor_start < 0:
                text_cursor_start = 0

            result = self.rtm.tasksNotes.add(timeline=self.timeline,
                                             list_id=self.rtm_list.id,
                                             taskseries_id=self.
                                             rtm_taskseries.id,
                                             task_id=self.rtm_task.id,
                                             note_title="",
                                             note_text=text[text_cursor_start:
                                                            text_cursor_end])
            transaction_ids.append(result.transaction.id)
            if text_cursor_start <= 0:
                break
            text_cursor_end = text_cursor_start - 1