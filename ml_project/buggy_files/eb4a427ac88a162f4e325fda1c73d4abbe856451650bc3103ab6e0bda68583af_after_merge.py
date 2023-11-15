def symlink_to(orig, dest):
    if is_windows:
        import subprocess
        subprocess.call(['mklink', '/d', path2str(orig), path2str(dest)], shell=True)
    else:
        orig.symlink_to(dest)