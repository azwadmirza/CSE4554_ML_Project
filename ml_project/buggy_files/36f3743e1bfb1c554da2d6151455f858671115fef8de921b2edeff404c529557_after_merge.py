def wait_for_exit(runner: Runner, main_process: Popen) -> None:
    """
    Monitor main process and background items until done
    """
    runner.write("Everything launched. Waiting to exit...")
    main_command = str_command(str(arg) for arg in main_process.args)
    span = runner.span()
    while True:
        sleep(0.1)
        main_code = main_process.poll()
        if main_code is not None:
            # Shell exited, we're done. Automatic shutdown cleanup will kill
            # subprocesses.
            runner.write(
                "Main process ({})\n exited with code {}.".format(
                    main_command, main_code
                )
            )
            span.end()
            runner.set_success(True)
            raise SystemExit(main_code)
        if runner.tracked:
            dead_bg = runner.tracked.which_dead()
        else:
            dead_bg = None
        if dead_bg:
            # Unfortunately torsocks doesn't deal well with connections
            # being lost, so best we can do is shut down.
            # FIXME: Look at bg.critical and do something smarter
            runner.show(
                "Proxy to Kubernetes exited. This is typically due to"
                " a lost connection."
            )
            span.end()
            raise runner.fail("Exiting...", code=3)