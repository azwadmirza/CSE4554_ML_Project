def retryOnAzureTimeout(exception):
    timeoutMsg = "could not be completed within the specified time"
    busyMsg = "Service Unavailable"
    return isinstance(exception, WindowsAzureError) and (timeoutMsg in str(exception)
        or busyMsg in str(exception))