def main(argv=None):  # noqa: C901
    """Run dvc CLI command.

    Args:
        argv: optional list of arguments to parse. sys.argv is used by default.

    Returns:
        int: command's return code.
    """
    args = None
    disable_other_loggers()

    outerLogLevel = logger.level
    try:
        args = parse_args(argv)

        level = None
        if args.quiet:
            level = logging.CRITICAL
        elif args.verbose == 1:
            level = logging.DEBUG
        elif args.verbose > 1:
            level = logging.TRACE

        if level is not None:
            logger.setLevel(level)

        logger.trace(args)

        with profile(enable=args.cprofile, dump=args.cprofile_dump):
            cmd = args.func(args)
            ret = cmd.run()
    except ConfigError:
        logger.exception("configuration error")
        ret = 251
    except KeyboardInterrupt:
        logger.exception("interrupted by the user")
        ret = 252
    except NotDvcRepoError:
        logger.exception("")
        ret = 253
    except DvcParserError:
        ret = 254
    except DvcException:
        ret = 255
        logger.exception("")
    except Exception as exc:  # noqa, pylint: disable=broad-except
        # pylint: disable=no-member
        if isinstance(exc, OSError) and exc.errno == errno.EMFILE:
            logger.exception(
                "too many open files, please visit "
                "{} to see how to handle this "
                "problem".format(error_link("many-files")),
                extra={"tb_only": True},
            )
        else:
            from dvc.info import get_dvc_info

            logger.exception("unexpected error")
            logger.info(FOOTER)
            dvc_info = get_dvc_info()
            logger.info(dvc_info)
        ret = 255

    try:
        if analytics.is_enabled():
            analytics.collect_and_send_report(args, ret)

        return ret
    finally:
        logger.setLevel(outerLogLevel)

        # Closing pools by-hand to prevent weird messages when closing SSH
        # connections. See https://github.com/iterative/dvc/issues/3248 for
        # more info.
        close_pools()

        # Remove cached repos in the end of the call, these are anonymous
        # so won't be reused by any other subsequent run anyway.
        clean_repos()