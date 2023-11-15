def main():
    ad_pids = []
    procs = []
    for p in psutil.process_iter():
        with p.oneshot():
            try:
                mem = p.memory_full_info()
                info = p.as_dict(["cmdline", "username"])
            except psutil.AccessDenied:
                ad_pids.append(p.pid)
            except psutil.NoSuchProcess:
                pass
            else:
                p._uss = mem.uss
                p._rss = mem.rss
                if not p._uss:
                    continue
                p._pss = getattr(mem, "pss", "")
                p._swap = getattr(mem, "swap", "")
                p._info = info
                procs.append(p)

    procs.sort(key=lambda p: p._uss)
    templ = "%-7s %-7s %7s %7s %7s %7s %7s"
    print(templ % ("PID", "User", "USS", "PSS", "Swap", "RSS", "Cmdline"))
    print("=" * 78)
    for p in procs[:86]:
        cmd = " ".join(p._info["cmdline"])[:50] if p._info["cmdline"] else ""
        line = templ % (
            p.pid,
            p._info["username"][:7] if p._info["username"] else "",
            convert_bytes(p._uss),
            convert_bytes(p._pss) if p._pss != "" else "",
            convert_bytes(p._swap) if p._swap != "" else "",
            convert_bytes(p._rss),
            cmd,
        )
        print(line)
    if ad_pids:
        print("warning: access denied for %s pids" % (len(ad_pids)),
              file=sys.stderr)