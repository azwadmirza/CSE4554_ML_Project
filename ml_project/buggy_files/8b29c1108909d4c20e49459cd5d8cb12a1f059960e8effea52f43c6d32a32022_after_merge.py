    def _interact_with_process(self, case, result, input):
        interactor = Interactor(self._current_proc)
        self.check = False
        self.feedback = None
        try:
            self.check = self.interact(case, interactor)
            interactor.close()
        except WrongAnswer as wa:
            self.feedback = str(wa)
        except IOError:
            pass

        self._current_proc.wait()
        return self._current_proc.stderr.read()