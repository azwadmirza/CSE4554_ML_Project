def copy_sample_file(app, filename, dest_path=None):
    """
    Copies a sample file at `filename` to `the dest_path`
    directory and strips the '.sample' extensions from `filename`.
    """
    if dest_path is None:
        dest_path = os.path.abspath(app.config.tool_data_path)
    sample_file_name = basic_util.strip_path(filename)
    copied_file = sample_file_name.rsplit('.sample', 1)[0]
    full_source_path = os.path.abspath(filename)
    full_destination_path = os.path.join(dest_path, sample_file_name)
    # Don't copy a file to itself - not sure how this happens, but sometimes it does...
    if full_source_path != full_destination_path:
        # It's ok to overwrite the .sample version of the file.
        shutil.copy(full_source_path, full_destination_path)
    # Only create the .loc file if it does not yet exist.  We don't overwrite it in case it
    # contains stuff proprietary to the local instance.
    if not os.path.lexists(os.path.join(dest_path, copied_file)):
        shutil.copy(full_source_path, os.path.join(dest_path, copied_file))