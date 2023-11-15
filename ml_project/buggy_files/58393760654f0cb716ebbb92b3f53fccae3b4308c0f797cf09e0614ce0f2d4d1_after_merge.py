def render_rules(ostream, doc):
    """
    like:

        ## rules
        check for OutputDebugString error
        namespace  anti-analysis/anti-debugging/debugger-detection
        author     michael.hunhoff@fireeye.com
        scope      function
        mbc        Anti-Behavioral Analysis::Detect Debugger::OutputDebugString
        examples   Practical Malware Analysis Lab 16-02.exe_:0x401020
        function @ 0x10004706
          and:
            api: kernel32.SetLastError @ 0x100047C2
            api: kernel32.GetLastError @ 0x10004A87
            api: kernel32.OutputDebugString @ 0x10004767, 0x10004787, 0x10004816, 0x10004895
    """
    had_match = False
    for rule in rutils.capability_rules(doc):
        count = len(rule["matches"])
        if count == 1:
            capability = rutils.bold(rule["meta"]["name"])
        else:
            capability = "%s (%d matches)" % (rutils.bold(rule["meta"]["name"]), count)

        ostream.writeln(capability)
        had_match = True

        rows = []
        for key in capa.rules.META_KEYS:
            if key == "name" or key not in rule["meta"]:
                continue

            v = rule["meta"][key]
            if isinstance(v, list) and len(v) == 1:
                v = v[0]
            elif isinstance(v, list) and len(v) > 1:
                v = ", ".join(v)
            rows.append((key, v))

        ostream.writeln(tabulate.tabulate(rows, tablefmt="plain"))

        if rule["meta"]["scope"] == capa.rules.FILE_SCOPE:
            matches = list(doc["rules"][rule["meta"]["name"]]["matches"].values())
            if len(matches) != 1:
                # i think there should only ever be one match per file-scope rule,
                # because we do the file-scope evaluation a single time.
                # but i'm not 100% sure if this is/will always be true.
                # so, lets be explicit about our assumptions and raise an exception if they fail.
                raise RuntimeError("unexpected file scope match count: %d" % (len(matches)))
            render_match(ostream, matches[0], indent=0)
        else:
            for location, match in sorted(doc["rules"][rule["meta"]["name"]]["matches"].items()):
                ostream.write(rule["meta"]["scope"])
                ostream.write(" @ ")
                ostream.writeln(rutils.hex(location))
                render_match(ostream, match, indent=1)
        ostream.write("\n")

    if not had_match:
        ostream.writeln(rutils.bold("no capabilities found"))