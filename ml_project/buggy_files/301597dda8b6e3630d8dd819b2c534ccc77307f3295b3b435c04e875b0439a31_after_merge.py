def print_stacks(file=sys.stderr):
    """Print current status of the process

    For debugging purposes.
    Used as part of SIGINFO handler.

    - Shows active thread count
    - Shows current stack for all threads

    Parameters:

    file: file to write output to (default: stderr)

    """
    # local imports because these will not be used often,
    # no need to add them to startup
    import asyncio
    import traceback
    from .log import coroutine_frames

    print("Active threads: %i" % threading.active_count(), file=file)
    for thread in threading.enumerate():
        print("Thread %s:" % thread.name, end='', file=file)
        frame = sys._current_frames()[thread.ident]
        stack = traceback.extract_stack(frame)
        if thread is threading.current_thread():
            # truncate last two frames of the current thread
            # which are this function and its caller
            stack = stack[:-2]
        stack = coroutine_frames(stack)
        if stack:
            last_frame = stack[-1]
            if (
                last_frame[0].endswith('threading.py')
                and last_frame[-1] == 'waiter.acquire()'
            ) or (
                last_frame[0].endswith('thread.py')
                and last_frame[-1].endswith('work_queue.get(block=True)')
            ):
                # thread is waiting on a condition
                # call it idle rather than showing the uninteresting stack
                # most threadpools will be in this state
                print(' idle', file=file)
                continue

        print(''.join(['\n'] + traceback.format_list(stack)), file=file)

    # also show asyncio tasks, if any
    # this will increase over time as we transition from tornado
    # coroutines to native `async def`
    tasks = asyncio_all_tasks()
    if tasks:
        print("AsyncIO tasks: %i" % len(tasks))
        for task in tasks:
            task.print_stack(file=file)