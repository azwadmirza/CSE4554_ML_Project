def main():
    # Glances - Init stuff
    ######################

    global config, limits, monitors, logs, stats, screen
    global htmloutput, csvoutput
    global html_tag, csv_tag, server_tag, client_tag
    global psutil_get_io_counter_tag, psutil_mem_vm
    global percpu_tag, fs_tag, diskio_tag, network_tag, network_bytepersec_tag
    global sensors_tag, hddtemp_tag, process_tag
    global refresh_time, client, server, server_port, server_ip
    global last_update_times

    # create update times dict
    last_update_times = {}

    # Set default tags
    percpu_tag = False
    fs_tag = True
    diskio_tag = True
    network_tag = True
    network_bytepersec_tag = False
    sensors_tag = False
    hddtemp_tag = False
    process_tag = True
    html_tag = False
    csv_tag = False
    client_tag = False
    password_tag = False
    password_prompt = False
    if is_Windows and not is_colorConsole:
        # Force server mode for Windows OS without colorconsole
        server_tag = True
    else:
        server_tag = False

    # Configuration file stuff
    conf_file = ""
    conf_file_tag = False

    # Set the default refresh time
    refresh_time = 3

    # Set the default cache lifetime (for server)
    cached_time = 1

    # Use curses.A_BOLD by default
    use_bold = True

    # Set the default TCP port for client and server
    server_port = 61209
    bind_ip = "0.0.0.0"

    # Default username/password
    username = "glances"
    password = ""

    # Manage options/arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "B:bdeymnho:f:t:vsc:p:C:P:zr1",
                                   ["bind", "bytepersec", "diskio", "mount",
                                    "sensors", "hddtemp", "netrate", "help",
                                    "output", "file", "time", "version",
                                    "server", "client", "port", "config",
                                    "password", "nobold", "noproc", "percpu"])
    except getopt.GetoptError as err:
        # Print help information and exit
        print(str(err))
        print(_("Try 'glances -h' for more information."))
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-v", "--version"):
            printVersion()
            sys.exit(0)
        elif opt in ("-s", "--server"):
            server_tag = True
        elif opt in ("-P"):
            password_tag = True
            password = arg
        elif opt in ("--password", "--password"):
            password_prompt = True
        elif opt in ("-B", "--bind"):
            bind_ip = arg
        elif opt in ("-c", "--client"):
            client_tag = True
            server_ip = arg
        elif opt in ("-p", "--port"):
            server_port = arg
        elif opt in ("-o", "--output"):
            if arg.lower() == "html":
                html_tag = True
            elif arg.lower() == "csv":
                csv_tag = True
            else:
                print(_("Error: Unknown output %s") % arg)
                sys.exit(2)
        elif opt in ("-e", "--sensors"):
            sensors_tag = True
        elif opt in ("-y", "--hddtemp"):
            hddtemp_tag = True
        elif opt in ("-f", "--folder"):
            output_folder = arg
        elif opt in ("-t", "--time"):
            if not (arg.isdigit() and int(arg) > 0):
                print(_("Error: Refresh time should be a positive integer"))
                sys.exit(2)
            refresh_time = int(arg)
        elif opt in ("-d", "--diskio"):
            diskio_tag = False
        elif opt in ("-m", "--mount"):
            fs_tag = False
        elif opt in ("-n", "--netrate"):
            network_tag = False
        elif opt in ("-b", "--bytepersec"):
            network_bytepersec_tag = True
        elif opt in ("-C", "--config"):
            conf_file = arg
            conf_file_tag = True
        elif opt in ("-z", "--nobold"):
            use_bold = False
        elif opt in ("-r", "--noproc"):
            process_tag = False
        elif opt in ("-1", "--percpu"):
            percpu_tag = True
        else:
            printSyntax()
            sys.exit(0)

    # Check options
    if password_tag and password_prompt:
        print(_("Error: Cannot use both -P and --password flag"))
        sys.exit(2)

    if server_tag:
        if client_tag:
            print(_("Error: Cannot use both -s and -c flag"))
            sys.exit(2)
        if html_tag or csv_tag:
            print(_("Error: Cannot use both -s and -o flag"))
            sys.exit(2)
        if password_prompt:
            password = get_password(description=_("Define the password for the Glances server"), confirm=True)

    if client_tag:
        if html_tag or csv_tag:
            print(_("Error: Cannot use both -c and -o flag"))
            sys.exit(2)
        if conf_file_tag:
            print(_("Error: Cannot use both -c and -C flag"))
            print(_("Limits are set based on the server ones"))
            sys.exit(2)
        if password_prompt:
            password = get_password(description=_("Enter the Glances server password"), confirm=False)

    if html_tag:
        if not html_lib_tag:
            print(_("Error: Need Jinja2 library to export into HTML"))
            sys.exit(2)
        try:
            output_folder
        except UnboundLocalError:
            print(_("Error: HTML export (-o html) need output folder definition (-f <folder>)"))
            sys.exit(2)

    if csv_tag:
        if not csv_lib_tag:
            print(_("Error: Need CSV library to export into CSV"))
            sys.exit(2)
        try:
            output_folder
        except UnboundLocalError:
            print(_("Error: CSV export (-o csv) need output folder definition (-f <folder>)"))
            sys.exit(2)

    # Catch CTRL-C
    signal.signal(signal.SIGINT, signal_handler)

    if conf_file_tag:
        config = Config(conf_file)
    else:
        config = Config()

    if client_tag:
        psutil_get_io_counter_tag = True
        psutil_mem_vm = False
        fs_tag = True
        diskio_tag = True
        network_tag = True
        sensors_tag = True
        hddtemp_tag = True
    elif server_tag:
        sensors_tag = True
        hddtemp_tag = True

    # Init Glances depending of the mode (standalone, client, server)
    if server_tag:
        # Init the server
        try:
            server = GlancesServer(bind_ip, int(server_port), GlancesXMLRPCHandler, cached_time)
        except (ValueError, socket.error) as err:
            print(_("Error: Invalid port number: %s") % err)
            sys.exit(2)
        print(_("Glances server is running on") + " %s:%s" % (bind_ip, server_port))

        # Set the server login/password (if -P/--password tag)
        if password != "":
            server.add_user(username, password)

        # Init Limits
        limits = glancesLimits()

        # Init monitor list
        monitors = monitorList()

        # Init stats
        stats = GlancesStatsServer()
        stats.update({})
    elif client_tag:
        # Init the client (displaying server stat in the CLI)
        try:
            client = GlancesClient(server_ip, int(server_port), username, password)
        except (ValueError, socket.error) as err:
            print(_("Error: Invalid port number: %s") % err)
            sys.exit(2)

        # Test if client and server are in the same major version
        if not client.client_init():
            print(_("Error: The server version is not compatible"))
            sys.exit(2)

        # Init Limits
        limits = glancesLimits()

        # Init monitor list
        monitors = monitorList()

        # Init Logs
        logs = glancesLogs()

        # Init stats
        stats = GlancesStatsClient()

        # Init screen
        screen = glancesScreen(refresh_time=refresh_time,
                               use_bold=use_bold)
    else:
        # Init the classical CLI

        # Init Limits
        limits = glancesLimits()

        # Init monitor list
        monitors = monitorList()

        # Init Logs
        logs = glancesLogs()

        # Init stats
        stats = GlancesStats()

        # Init HTML output
        if html_tag:
            htmloutput = glancesHtml(html_path=output_folder,
                                     refresh_time=refresh_time)

        # Init CSV output
        if csv_tag:
            csvoutput = glancesCsv(csv_path=output_folder,
                                   refresh_time=refresh_time)

        # Init screen
        screen = glancesScreen(refresh_time=refresh_time,
                               use_bold=use_bold)

    # Glances - Main loop
    #####################

    if server_tag:
        # Start the server loop
        server.serve_forever()
    elif client_tag:
        # Set the limits to the server ones
        server_limits = client.client_get_limits()
        if server_limits != {}:
            limits.setAll(server_limits)

        # Set the monitored pocesses list to the server one
        server_monitored = client.client_get_monitored()
        if server_monitored != []:
            monitors.setAll(server_monitored)

        # Start the client (CLI) loop
        while True:
            # Get server system informations
            server_stats = client.client_get()
            if server_stats == {}:
                server_status = "Disconnected"
            else:
                server_status = "Connected"
                stats.update(server_stats)
            # Update the screen
            screen.update(stats, cs_status=server_status)
    else:
        # Start the standalone (CLI) loop
        while True:
            # Get system informations
            stats.update()

            # Update the screen
            screen.update(stats)

            # Update the HTML output
            if html_tag:
                htmloutput.update(stats)

            # Update the CSV output
            if csv_tag:
                csvoutput.update(stats)