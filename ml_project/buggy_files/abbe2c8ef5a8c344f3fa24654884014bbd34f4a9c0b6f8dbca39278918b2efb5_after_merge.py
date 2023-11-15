def _validate_args(parser, options, args):
    # validate args first so we don't spin up any resources
    if options.child_name:
        if not options.server_uri:
            parser.error("--child option requires --server_uri to be set as well")
        if not options.run_id:
            parser.error("--child option requires --run_id to be set as well")                
        if options.port:
            parser.error("port option cannot be used with roslaunch child mode")
        if args:
            parser.error("Input files are not allowed when run in child mode")
    elif options.core:
        if args:
            parser.error("Input files are not allowed when launching core")
        if options.run_id:
            parser.error("--run_id should only be set for child roslaunches (-c)")
                
        # we don't actually do anything special for core as the roscore.xml file
        # is an implicit include for any roslaunch

    elif len(args) == 0:
        parser.error("you must specify at least one input file")
    else:
        missing_files = [f for f in args if not (f == '-' or os.path.exists(f))]
        if missing_files:
            parser.error("The following input files do not exist: %s"%', '.join(missing_files))

    if args.count('-') > 1:
        parser.error("Only a single instance of the dash ('-') may be specified.")

    if len([x for x in [options.node_list, options.find_node, options.node_args, options.ros_args] if x]) > 1:
        parser.error("only one of [--nodes, --find-node, --args --ros-args] may be specified")