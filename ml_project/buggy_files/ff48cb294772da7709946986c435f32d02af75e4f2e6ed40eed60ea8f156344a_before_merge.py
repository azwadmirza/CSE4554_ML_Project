    def dotnet_notification_parser(sender: Any, data: Any):
        # Return only the UUID string representation as sender.
        # Also do a conversion from System.Bytes[] to bytearray.
        return func(sender.Uuid.ToString(), bytearray(data))