def send_command():
    """
    Run a remote command. This is called via py3-cmd utility.

    We look for any uds sockets with the correct name prefix and send our
    command to all that we find.  This allows us to communicate with multiple
    py3status instances.
    """

    def verbose(msg):
        """
        print output if verbose is set.
        """
        if options.verbose:
            print(msg)

    options = command_parser()
    msg = json.dumps(vars(options)).encode("utf-8")
    if len(msg) > MAX_SIZE:
        verbose(f"Message length too long, max length ({MAX_SIZE})")

    # find all likely socket addresses
    uds_list = Path(SERVER_ADDRESS).parent.glob(f"{Path(SERVER_ADDRESS).name}.[0-9]*")

    verbose(f"message {msg!r}")
    for uds in uds_list:
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        verbose(f"connecting to {uds}")
        try:
            sock.connect(uds.as_posix())
        except OSError:
            # this is a stale socket so delete it
            verbose("stale socket deleting")
            try:
                uds.unlink()
            except OSError:
                pass
            continue
        try:
            # Send data
            verbose("sending")
            sock.sendall(msg)
        finally:
            verbose("closing socket")
            sock.close()