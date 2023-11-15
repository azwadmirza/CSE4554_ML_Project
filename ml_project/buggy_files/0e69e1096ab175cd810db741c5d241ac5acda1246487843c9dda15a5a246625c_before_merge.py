def main():
    try:
        _setup()
        return _run_queuer()
    except SystemExit as exit_code:
        sys.exit(exit_code)
    except:
        LOG.exception('(PID=%s) Scheduler quit due to exception.', os.getpid())
        return 1
    finally:
        _teardown()