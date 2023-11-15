def rosmsg_cmd_show(mode, full, alias='show'):
    cmd = "ros%s"%(mode[1:])
    parser = OptionParser(usage="usage: %s %s [options] <%s>"%(cmd, alias, full))
    parser.add_option("-r", "--raw",
                      dest="raw", default=False,action="store_true",
                      help="show raw message text, including comments")
    parser.add_option("-b", "--bag",
                      dest="bag", default=None,
                      help="show message from .bag file", metavar="BAGFILE")
    options, arg = _stdin_arg(parser, full)
    if arg.endswith(mode):
        arg = arg[:-(len(mode))]

    # try to catch the user specifying code-style types and error
    if '::' in arg:
        parser.error(cmd+" does not understand C++-style namespaces (i.e. '::').\nPlease refer to msg/srv types as 'package_name/Type'.")
    elif '.' in arg:
        parser.error("invalid message type '%s'.\nPlease refer to msg/srv types as 'package_name/Type'." % arg)
    if options.bag:
        bag_file = options.bag
        if not os.path.exists(bag_file):
            raise ROSMsgException("ERROR: bag file [%s] does not exist"%bag_file)
        for topic, msg, t in rosbag.Bag(bag_file).read_messages(raw=True):
            datatype, _, _, _, pytype = msg
            if datatype == arg:
                if options.raw:
                    print(pytype._full_text)
                else:
                    context = genmsg.MsgContext.create_default()
                    msgs = generate_dynamic(datatype, pytype._full_text)
                    for t, msg in msgs.items():
                        context.register(t, msg._spec)
                    print(spec_to_str(context, msgs[datatype]._spec))
                break
    else:
        rospack = rospkg.RosPack()
        if '/' in arg: #package specified
            rosmsg_debug(rospack, mode, arg, options.raw)
        else:
            found_msgs = list(rosmsg_search(rospack, mode, arg))
            if not found_msgs:
                print("Could not find msg '%s'" % arg, file=sys.stderr)
                return 1
            for found in found_msgs:
                print("[%s]:"%found)
                rosmsg_debug(rospack, mode, found, options.raw)