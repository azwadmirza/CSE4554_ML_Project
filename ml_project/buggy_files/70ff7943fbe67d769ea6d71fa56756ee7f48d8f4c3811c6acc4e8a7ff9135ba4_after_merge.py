def link_or_copy_directory(src, dst):
    try:
        copytree(src, dst, copy_function=os.link, dirs_exist_ok=True)
    except OSError:
        copytree(src, dst, dirs_exist_ok=True)