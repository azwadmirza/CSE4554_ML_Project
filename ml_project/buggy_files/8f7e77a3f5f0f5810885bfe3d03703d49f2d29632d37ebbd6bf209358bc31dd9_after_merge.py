def main(argv=sys.argv):
    options = None
    logger = None
    try:
        from . import rlutil
        parser = _get_optparse()
        
        (options, args) = parser.parse_args(argv[1:])
        args = rlutil.resolve_launch_arguments(args)
        _validate_args(parser, options, args)

        # node args doesn't require any roslaunch infrastructure, so process it first
        if any([options.node_args, options.node_list, options.find_node, options.dump_params, options.file_list, options.ros_args]):
            if options.node_args and not args:
                parser.error("please specify a launch file")

            from . import node_args
            if options.node_args:
                node_args.print_node_args(options.node_args, args)
            elif options.find_node:
                node_args.print_node_filename(options.find_node, args)
            # Dump parameters, #2685
            elif options.dump_params:
                roslaunch_param_dump.dump_params(args)
            elif options.file_list:
                rlutil.print_file_list(args)
            elif options.ros_args:
                import arg_dump as roslaunch_arg_dump
                roslaunch_arg_dump.dump_args(args)
            else:
                node_args.print_node_list(args)
            return

        # we have to wait for the master here because we don't have the run_id yet
        if options.wait_for_master:
            if options.core:
                parser.error("--wait cannot be used with roscore")
            rlutil._wait_for_master()            

        # write the pid to a file
        write_pid_file(options.pid_fn, options.core, options.port)

        # spin up the logging infrastructure. have to wait until we can read options.run_id
        uuid = rlutil.get_or_generate_uuid(options.run_id, options.wait_for_master)
        configure_logging(uuid)

        # #3088: don't check disk usage on remote machines
        if not options.child_name and not options.skip_log_check:
            # #2761
            rlutil.check_log_disk_usage()

        logger = logging.getLogger('roslaunch')
        logger.info("roslaunch starting with args %s"%str(argv))
        logger.info("roslaunch env is %s"%os.environ)
            
        if options.child_name:
            logger.info('starting in child mode')

            # This is a roslaunch child, spin up client server.
            # client spins up an XML-RPC server that waits for
            # commands and configuration from the server.
            from . import child as roslaunch_child
            c = roslaunch_child.ROSLaunchChild(uuid, options.child_name, options.server_uri)
            c.run()
        else:
            logger.info('starting in server mode')

            # #1491 change terminal name
            if not options.disable_title:
                rlutil.change_terminal_name(args, options.core)
            
            # Read roslaunch string from stdin when - is passed as launch filename.
            roslaunch_strs = []
            if '-' in args:
                roslaunch_core.printlog("Passed '-' as file argument, attempting to read roslaunch XML from stdin.")
                roslaunch_strs.append(sys.stdin.read())
                roslaunch_core.printlog("... %d bytes read successfully.\n" % len(roslaunch_strs[-1]))
                args.remove('-')

            # This is a roslaunch parent, spin up parent server and launch processes.
            # args are the roslaunch files to load
            from . import parent as roslaunch_parent
            try:
                # force a port binding spec if we are running a core
                if options.core:
                    options.port = options.port or DEFAULT_MASTER_PORT
                p = roslaunch_parent.ROSLaunchParent(uuid, args, roslaunch_strs=roslaunch_strs,
                        is_core=options.core, port=options.port, local_only=options.local_only,
                        verbose=options.verbose, force_screen=options.force_screen)
                p.start()
                p.spin()
            finally:
                # remove the pid file
                if options.pid_fn:
                    try: os.unlink(options.pid_fn)
                    except os.error: pass

    except RLException as e:
        roslaunch_core.printerrlog(str(e))
        roslaunch_core.printerrlog('The traceback for the exception was written to the log file')
        if logger:
            logger.error(traceback.format_exc())
        sys.exit(1)
    except ValueError as e:
        # TODO: need to trap better than this high-level trap
        roslaunch_core.printerrlog(str(e))
        roslaunch_core.printerrlog('The traceback for the exception was written to the log file')
        if logger:
            logger.error(traceback.format_exc())
        sys.exit(1)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)