def retryOnAzureTimeout(exception):
    timeoutMsg = "could not be completed within the specified time"
    return isinstance(exception, WindowsAzureError) and timeoutMsg in str(exception)