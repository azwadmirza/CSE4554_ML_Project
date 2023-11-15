def _git_toplevel(path):
    try:
        with open(os.devnull, "wb") as devnull:
            out = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=(path or "."),
                universal_newlines=True,
                stderr=devnull,
            )
        trace("find files toplevel", out)
        return os.path.normcase(os.path.realpath(out.strip()))
    except subprocess.CalledProcessError:
        # git returned error, we are not in a git repo
        return None
    except OSError:
        # git command not found, probably
        return None