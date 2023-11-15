def create_archive(git_path, module, dest, archive, version, repo, result):
    """ Helper function for creating archive using git_archive """
    all_archive_fmt = {'.zip': 'zip', '.gz': 'tar.gz', '.tar': 'tar',
                       '.tgz': 'tgz'}
    _, archive_ext = os.path.splitext(archive)
    archive_fmt = all_archive_fmt.get(archive_ext, None)
    if archive_fmt is None:
        module.fail_json(msg="Unable to get file extension from "
                             "archive file name : %s" % archive,
                         details="Please specify archive as filename with "
                                 "extension. File extension can be one "
                                 "of ['tar', 'tar.gz', 'zip', 'tgz']")

    repo_name = repo.split("/")[-1].replace(".git", "")

    if os.path.exists(archive):
        # If git archive file exists, then compare it with new git archive file.
        # if match, do nothing
        # if does not match, then replace existing with temp archive file.
        tempdir = tempfile.mkdtemp()
        new_archive_dest = os.path.join(tempdir, repo_name)
        new_archive = new_archive_dest + '.' + archive_fmt
        git_archive(git_path, module, dest, new_archive, archive_fmt, version)

        # filecmp is supposed to be efficient than md5sum checksum
        if filecmp.cmp(new_archive, archive):
            result.update(changed=False)
            # Cleanup before exiting
            try:
                shutil.rmtree(tempdir)
            except OSError:
                pass
        else:
            try:
                shutil.move(new_archive, archive)
                shutil.rmtree(tempdir)
                result.update(changed=True)
            except OSError as e:
                module.fail_json(msg="Failed to move %s to %s" %
                                     (new_archive, archive),
                                 details="Error occured while moving : %s"
                                         % to_native(e))
    else:
        # Perform archive from local directory
        git_archive(git_path, module, dest, archive, archive_fmt, version)
        result.update(changed=True)