def _notification_wrapper(func: Callable):
    @wraps(func)
    def dotnet_notification_parser(sender: Any, args: Any):
        # Return only the UUID string representation as sender.
        # Also do a conversion from System.Bytes[] to bytearray.
        reader = DataReader.FromBuffer(args.CharacteristicValue)
        output = Array[Byte]([0] * reader.UnconsumedBufferLength)
        reader.ReadBytes(output)

        return func(sender.Uuid.ToString(), bytearray(output))

    return dotnet_notification_parser