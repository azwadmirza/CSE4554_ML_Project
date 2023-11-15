def copy_file(source_path, output_path):
    """
    Copy source_path to output_path, making sure any parent directories exist.

    The output_path may be a directory.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, os.path.basename(source_path))
    shutil.copyfile(source_path, output_path)