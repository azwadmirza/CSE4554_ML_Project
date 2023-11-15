def reformat_many(
    sources: Set[Path], fast: bool, write_back: WriteBack, mode: Mode, report: "Report"
) -> None:
    """Reformat multiple files using a ProcessPoolExecutor."""
    loop = asyncio.get_event_loop()
    worker_count = os.cpu_count()
    if sys.platform == "win32":
        # Work around https://bugs.python.org/issue26903
        worker_count = min(worker_count, 61)
    try:
        executor = ProcessPoolExecutor(max_workers=worker_count)
    except OSError:
        # we arrive here if the underlying system does not support multi-processing
        # like in AWS Lambda, in which case we gracefully fallback to the default
        # mono-process Executor by using None
        executor = None

    try:
        loop.run_until_complete(
            schedule_formatting(
                sources=sources,
                fast=fast,
                write_back=write_back,
                mode=mode,
                report=report,
                loop=loop,
                executor=executor,
            )
        )
    finally:
        shutdown(loop)
        if executor is not None:
            executor.shutdown()