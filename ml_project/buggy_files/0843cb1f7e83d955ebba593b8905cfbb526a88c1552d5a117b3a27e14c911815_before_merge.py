def _git_ls_files_and_dirs(toplevel):
    # use git archive instead of git ls-file to honor
    # export-ignore git attribute
    cmd = ["git", "archive", "--prefix", toplevel + os.path.sep, "HEAD"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=toplevel)
    tf = tarfile.open(fileobj=proc.stdout, mode="r|*")
    git_files = set()
    git_dirs = {toplevel}
    for member in tf.getmembers():
        name = os.path.normcase(member.name).replace("/", os.path.sep)
        if member.type == tarfile.DIRTYPE:
            git_dirs.add(name)
        else:
            git_files.add(name)
    return git_files, git_dirs