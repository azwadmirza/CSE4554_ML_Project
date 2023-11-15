def list_tags(cwd):
    out, err = run_cmd(cwd, ['git', 'tag', '--list'], env={'LC_ALL': 'C'})
    tags = out.decode('utf-8').strip().split("\n")
    return tags