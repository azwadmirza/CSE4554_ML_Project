    def get_next_subject(self) -> Subject:
        # A StopIteration exception is expected when the queue is empty
        try:
            subject = next(self.subjects_iterable)
        except StopIteration as exception:
            self._print('Queue is empty:', exception)
            self.subjects_iterable = self.get_subjects_iterable()
            subject = next(self.subjects_iterable)
        return subject