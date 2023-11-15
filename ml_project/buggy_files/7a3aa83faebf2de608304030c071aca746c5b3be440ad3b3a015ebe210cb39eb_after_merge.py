def on_shutdown(
    manager: TaskManager, unsaved_jobs_lock: Lock
) -> Callable[[signal.Signals, Any], None]:
    def actual_callback(s: signal.Signals, __: Any) -> None:
        global shutting_down
        manager.logger.error("Got interupted by %r, shutting down", s)
        with unsaved_jobs_lock:
            shutting_down = True
        manager.close(relaxed=False)
        sys.exit(1)

    return actual_callback