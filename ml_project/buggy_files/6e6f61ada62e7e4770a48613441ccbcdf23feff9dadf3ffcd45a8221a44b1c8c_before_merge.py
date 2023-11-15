def main():
    red = None  # Error handling for users misusing the bot
    cli_flags = parse_cli_flags(sys.argv[1:])
    handle_early_exit_flags(cli_flags)
    if cli_flags.edit:
        handle_edit(cli_flags)
        return
    try:
        loop = asyncio.get_event_loop()

        if cli_flags.no_instance:
            print(
                "\033[1m"
                "Warning: The data will be placed in a temporary folder and removed on next system "
                "reboot."
                "\033[0m"
            )
            cli_flags.instance_name = "temporary_red"
            data_manager.create_temp_config()

        data_manager.load_basic_configuration(cli_flags.instance_name)

        red = Red(
            cli_flags=cli_flags, description="Red V3", dm_help=None, fetch_offline_members=True
        )

        if os.name != "nt":
            # None of this works on windows.
            # At least it's not a redundant handler...
            signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
            for s in signals:
                loop.add_signal_handler(
                    s, lambda s=s: asyncio.create_task(shutdown_handler(red, s))
                )

        exc_handler = functools.partial(global_exception_handler, red)
        loop.set_exception_handler(exc_handler)
        # We actually can't (just) use asyncio.run here
        # We probably could if we didnt support windows, but we might run into
        # a scenario where this isn't true if anyone works on RPC more in the future
        fut = loop.create_task(run_bot(red, cli_flags))
        r_exc_handler = functools.partial(red_exception_handler, red)
        fut.add_done_callback(r_exc_handler)
        loop.run_forever()
    except KeyboardInterrupt:
        # We still have to catch this here too. (*joy*)
        log.warning("Please do not use Ctrl+C to Shutdown Red! (attempting to die gracefully...)")
        log.error("Received KeyboardInterrupt, treating as interrupt")
        if red is not None:
            loop.run_until_complete(shutdown_handler(red, signal.SIGINT))
    except SystemExit as exc:
        # We also have to catch this one here. Basically any exception which normally
        # Kills the python interpreter (Base Exceptions minus asyncio.cancelled)
        # We need to do something with prior to having the loop close
        log.info("Shutting down with exit code: %s", exc.code)
        if red is not None:
            loop.run_until_complete(shutdown_handler(red, None, exc.code))
    finally:
        # Allows transports to close properly, and prevent new ones from being opened.
        # Transports may still not be closed correcly on windows, see below
        loop.run_until_complete(loop.shutdown_asyncgens())
        if os.name == "nt":
            # *we* aren't cleaning up more here, but it prevents
            # a runtime error at the event loop on windows
            # with resources which require longer to clean up.
            # With other event loops, a failure to cleanup prior to here
            # results in a resource warning instead and does not break us.
            log.info("Please wait, cleaning up a bit more")
            loop.run_until_complete(asyncio.sleep(1))
        loop.stop()
        loop.close()
        exit_code = red._shutdown_mode if red is not None else 1
        sys.exit(exit_code)