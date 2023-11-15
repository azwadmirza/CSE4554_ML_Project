def copy_file(source_path, output_path):
    """
    Copy source_path to output_path, making sure any parent directories exist.
    """

    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    shutil.copy(source_path, output_path)