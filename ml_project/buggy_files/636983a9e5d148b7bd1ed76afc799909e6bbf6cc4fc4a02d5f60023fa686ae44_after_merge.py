def link_or_copy_directory(src, dst):
    try:
        shutil.copytree(src, dst, copy_function=os.link, dirs_exist_ok=True)
    except OSError:
        shutil.copytree(src, dst, dirs_exist_ok=True)