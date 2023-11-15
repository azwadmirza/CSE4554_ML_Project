def get_git_url(dockerfile_path):
    '''Given a dockerfile_path, return url of git project which contains
    the dockerfile in a form of list.'''
    # get the path of the folder containing the dockerfile
    dockerfile_folder_path = os.path.dirname(os.path.abspath(dockerfile_path))
    command = ['git', 'remote', '-v']
    try:
        output = subprocess.check_output(  # nosec
            command, stderr=subprocess.DEVNULL, cwd=dockerfile_folder_path)
        if isinstance(output, bytes):
            lines = output.decode('utf-8').split('\n')
            # pop the last line which is an empty line
            lines.pop()
            url_list = set()
            for line in lines:
                extract_url = extract_git_url_from_line(line)
                if extract_url:
                    url_list.add(extract_url)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.debug("Cannot find git repo url, path is %s",
                     dockerfile_folder_path)
    return url_list