    def result(self):
        # TODO: Handle IsCancelled.
        if self.task.IsFaulted:
            # Exception occurred. Wrap it in BleakDotNetTaskError
            # to make it catchable.
            raise BleakDotNetTaskError(self.task.Exception.ToString())

        return self.task.Result