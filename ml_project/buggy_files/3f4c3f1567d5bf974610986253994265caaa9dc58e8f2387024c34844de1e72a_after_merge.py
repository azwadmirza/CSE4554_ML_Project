    def result(self):
        if self.operation.Status == AsyncStatus.Completed:
            return self.operation.GetResults()
        elif self.operation.Status == AsyncStatus.Error:
            # Exception occurred. Wrap it in BleakDotNetTaskError
            # to make it catchable.
            raise BleakDotNetTaskError(self.operation.ErrorCode.ToString())
        else:
            # TODO: Handle IsCancelled.
            raise BleakDotNetTaskError(
                "IAsyncOperation Status: {0}".format(self.operation.Status)
            )