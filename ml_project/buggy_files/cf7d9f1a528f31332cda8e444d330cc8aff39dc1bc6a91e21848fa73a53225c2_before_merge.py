async def wrap_IAsyncOperation(op, return_type, loop):
    """Enables await on .NET Task using asyncio.Event and a lambda callback.

    Args:
        task (System.Threading.Tasks.Task): .NET async task object
        to await upon.
        loop (Event Loop): The event loop to await on the Task in.

    Returns:
        The results of the the .NET Task.

    """
    done = asyncio.Event()
    # Register AsyncOperationCompletedHandler callback that triggers the above asyncio.Event.
    op.Completed = AsyncOperationCompletedHandler[return_type](
        lambda x, y: loop.call_soon_threadsafe(done.set)
    )
    # Wait for callback.
    await done.wait()

    if op.Status == AsyncStatus.Completed:
        return op.GetResults()
    elif op.Status == AsyncStatus.Error:
        # Exception occurred. Wrap it in BleakDotNetTaskError
        # to make it catchable.
        raise BleakDotNetTaskError(op.ErrorCode.ToString())
    else:
        # TODO: Handle IsCancelled.
        raise BleakDotNetTaskError("IAsyncOperation Status: {0}".format(op.Status))