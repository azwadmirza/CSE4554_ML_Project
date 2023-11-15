def check_git_src(dockerfile_path):
    '''Given the src_path and the dockerfile path, return the git
    repository name and sha information in the format of string.
    Currently we only consider the following situation:
    - target_git_project
        - dir1
        - dir2/dockerfile
    So we only use dockerfile_path to find the git repo info.'''
    # get the path of the folder containing the dockerfile
    dockerfile_folder_path = os.path.dirname(dockerfile_path)
    # locate the top level directory
    path_to_toplevel = get_git_toplevel(dockerfile_folder_path)
    # get the path of the target folder or file
    logger.debug('looking into path: %s for git repo.', path_to_toplevel)
    comment_line = ''
    if path_to_toplevel:
        sha_info = get_git_sha(path_to_toplevel)
        # if path_to_toplevel exists, name_info should be the folder name
        name_info = os.path.basename(path_to_toplevel)
        comment_line = ('git project name: ' + name_info +
                        ', HEAD sha: ' + sha_info)
    else:
        comment_line = 'Not a git repository'
    return comment_line