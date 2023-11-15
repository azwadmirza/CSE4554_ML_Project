def get_shellcode_vw(sample, arch="auto", should_save=True):
    """
    Return shellcode workspace using explicit arch or via auto detect
    """
    import viv_utils

    with open(sample, "rb") as f:
        sample_bytes = f.read()
    if arch == "auto":
        # choose arch with most functions, idea by Jay G.
        vw_cands = []
        for arch in ["i386", "amd64"]:
            vw_cands.append(
                viv_utils.getShellcodeWorkspace(sample_bytes, arch, base=SHELLCODE_BASE, should_save=should_save)
            )
        if not vw_cands:
            raise ValueError("could not generate vivisect workspace")
        vw = max(vw_cands, key=lambda vw: len(vw.getFunctions()))
    else:
        vw = viv_utils.getShellcodeWorkspace(sample_bytes, arch, base=SHELLCODE_BASE, should_save=should_save)

    vw.setMeta("StorageName", "%s.viv" % sample)

    return vw