def _git_ls_files_and_dirs(toplevel):
    # use git archive instead of git ls-file to honor
    # export-ignore git attribute
    cmd = ["git", "archive", "--prefix", toplevel + os.path.sep, "HEAD"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=toplevel)
    try:
        return _git_interpret_archive(proc.stdout, toplevel)
    except Exception:
        if proc.wait() != 0:
            log.exception("listing git files failed - pretending there aren't any")
        return (), ()