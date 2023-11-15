def tcpdump(pktlist, dump=False, getfd=False, args=None,
            prog=None, getproc=False, quiet=False, use_tempfile=None,
            read_stdin_opts=None, linktype=None, wait=True):
    """Run tcpdump or tshark on a list of packets.

    When using ``tcpdump`` on OSX (``prog == conf.prog.tcpdump``), this uses a
    temporary file to store the packets. This works around a bug in Apple's
    version of ``tcpdump``: http://apple.stackexchange.com/questions/152682/

    Otherwise, the packets are passed in stdin.

    This function can be explicitly enabled or disabled with the
    ``use_tempfile`` parameter.

    When using ``wireshark``, it will be called with ``-ki -`` to start
    immediately capturing packets from stdin.

    Otherwise, the command will be run with ``-r -`` (which is correct for
    ``tcpdump`` and ``tshark``).

    This can be overridden with ``read_stdin_opts``. This has no effect when
    ``use_tempfile=True``, or otherwise reading packets from a regular file.

pktlist: a Packet instance, a PacketList instance or a list of Packet
         instances. Can also be a filename (as a string), an open
         file-like object that must be a file format readable by
         tshark (Pcap, PcapNg, etc.) or None (to sniff)

dump:    when set to True, returns a string instead of displaying it.
getfd:   when set to True, returns a file-like object to read data
         from tcpdump or tshark from.
getproc: when set to True, the subprocess.Popen object is returned
args:    arguments (as a list) to pass to tshark (example for tshark:
         args=["-T", "json"]).
prog:    program to use (defaults to tcpdump, will work with tshark)
quiet:   when set to True, the process stderr is discarded
use_tempfile: When set to True, always use a temporary file to store packets.
              When set to False, pipe packets through stdin.
              When set to None (default), only use a temporary file with
              ``tcpdump`` on OSX.
read_stdin_opts: When set, a list of arguments needed to capture from stdin.
                 Otherwise, attempts to guess.
linktype: A custom DLT value or name, to overwrite the default values.
wait: If True (default), waits for the process to terminate before returning
      to Scapy. If False, the process will be detached to the background. If
      dump, getproc or getfd is True, these have the same effect as
      ``wait=False``.

Examples:

>>> tcpdump([IP()/TCP(), IP()/UDP()])
reading from file -, link-type RAW (Raw IP)
16:46:00.474515 IP 127.0.0.1.20 > 127.0.0.1.80: Flags [S], seq 0, win 8192, length 0  # noqa: E501
16:46:00.475019 IP 127.0.0.1.53 > 127.0.0.1.53: [|domain]

>>> tcpdump([IP()/TCP(), IP()/UDP()], prog=conf.prog.tshark)
  1   0.000000    127.0.0.1 -> 127.0.0.1    TCP 40 20->80 [SYN] Seq=0 Win=8192 Len=0  # noqa: E501
  2   0.000459    127.0.0.1 -> 127.0.0.1    UDP 28 53->53 Len=0

To get a JSON representation of a tshark-parsed PacketList(), one can:
>>> import json, pprint
>>> json_data = json.load(tcpdump(IP(src="217.25.178.5", dst="45.33.32.156"),
...                               prog=conf.prog.tshark, args=["-T", "json"],
...                               getfd=True))
>>> pprint.pprint(json_data)
[{u'_index': u'packets-2016-12-23',
  u'_score': None,
  u'_source': {u'layers': {u'frame': {u'frame.cap_len': u'20',
                                      u'frame.encap_type': u'7',
[...]
                                      u'frame.time_relative': u'0.000000000'},
                           u'ip': {u'ip.addr': u'45.33.32.156',
                                   u'ip.checksum': u'0x0000a20d',
[...]
                                   u'ip.ttl': u'64',
                                   u'ip.version': u'4'},
                           u'raw': u'Raw packet data'}},
  u'_type': u'pcap_file'}]
>>> json_data[0]['_source']['layers']['ip']['ip.ttl']
u'64'
    """
    getfd = getfd or getproc
    if prog is None:
        prog = [conf.prog.tcpdump]
        _prog_name = "windump()" if WINDOWS else "tcpdump()"
    elif isinstance(prog, six.string_types):
        _prog_name = "{}()".format(prog)
        prog = [prog]
    else:
        raise ValueError("prog must be a string")
    if prog[0] == conf.prog.tcpdump and not TCPDUMP:
        message = "tcpdump is not available. Cannot use tcpdump() !"
        raise Scapy_Exception(message)

    if linktype is not None:
        # Tcpdump does not support integers in -y (yet)
        # https://github.com/the-tcpdump-group/tcpdump/issues/758
        if isinstance(linktype, int):
            # Guess name from value
            try:
                linktype_name = _guess_linktype_name(linktype)
            except StopIteration:
                linktype = -1
        else:
            # Guess value from name
            if linktype.startswith("DLT_"):
                linktype = linktype[4:]
            linktype_name = linktype
            try:
                linktype = _guess_linktype_value(linktype)
            except KeyError:
                linktype = -1
        if linktype == -1:
            raise ValueError(
                "Unknown linktype. Try passing its datalink name instead"
            )
        prog += ["-y", linktype_name]

    # Build Popen arguments
    if args is None:
        args = []
    else:
        # Make a copy of args
        args = list(args)

    stdout = subprocess.PIPE if dump or getfd else None
    stderr = open(os.devnull) if quiet else None

    if use_tempfile is None:
        # Apple's tcpdump cannot read from stdin, see:
        # http://apple.stackexchange.com/questions/152682/
        use_tempfile = DARWIN and prog[0] == conf.prog.tcpdump

    if read_stdin_opts is None:
        if prog[0] == conf.prog.wireshark:
            # Start capturing immediately (-k) from stdin (-i -)
            read_stdin_opts = ["-ki", "-"]
        else:
            read_stdin_opts = ["-r", "-"]
    else:
        # Make a copy of read_stdin_opts
        read_stdin_opts = list(read_stdin_opts)

    if pktlist is None:
        # sniff
        with ContextManagerSubprocess(_prog_name, prog[0]):
            proc = subprocess.Popen(
                prog + args,
                stdout=stdout,
                stderr=stderr,
            )
    elif isinstance(pktlist, six.string_types):
        # file
        with ContextManagerSubprocess(_prog_name, prog[0]):
            proc = subprocess.Popen(
                prog + ["-r", pktlist] + args,
                stdout=stdout,
                stderr=stderr,
            )
    elif use_tempfile:
        tmpfile = get_temp_file(autoext=".pcap", fd=True)
        try:
            tmpfile.writelines(iter(lambda: pktlist.read(1048576), b""))
        except AttributeError:
            wrpcap(tmpfile, pktlist, linktype=linktype)
        else:
            tmpfile.close()
        with ContextManagerSubprocess(_prog_name, prog[0]):
            proc = subprocess.Popen(
                prog + ["-r", tmpfile.name] + args,
                stdout=stdout,
                stderr=stderr,
            )
    else:
        # pass the packet stream
        with ContextManagerSubprocess(_prog_name, prog[0]):
            proc = subprocess.Popen(
                prog + read_stdin_opts + args,
                stdin=subprocess.PIPE,
                stdout=stdout,
                stderr=stderr,
            )
        try:
            proc.stdin.writelines(iter(lambda: pktlist.read(1048576), b""))
        except AttributeError:
            wrpcap(proc.stdin, pktlist, linktype=linktype)
        except UnboundLocalError:
            raise IOError("%s died unexpectedly !" % prog)
        else:
            proc.stdin.close()
    if dump:
        return b"".join(iter(lambda: proc.stdout.read(1048576), b""))
    if getproc:
        return proc
    if getfd:
        return proc.stdout
    if wait:
        proc.wait()