def run_subs_scripts(video_path, scripts, *args):
    """Execute subtitle scripts.

    :param video_path: the video path
    :type video_path: str
    :param scripts: the script commands to be executed
    :type scripts: list of str
    :param args: the arguments to be passed to the script
    :type args: list of str
    """
    for script_name in scripts:
        script_cmd = [piece for piece in re.split("( |\\\".*?\\\"|'.*?')", script_name) if piece.strip()]
        script_cmd.extend(str(arg) for arg in args)

        logger.info(u'Running subtitle %s-script: %s', 'extra' if len(args) > 1 else 'pre', script_name)

        # use subprocess to run the command and capture output
        logger.info(u'Executing command: %s', script_cmd)
        try:
            process = subprocess.Popen(script_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, cwd=sickbeard.PROG_DIR)
            out, _ = process.communicate()  # @UnusedVariable
            logger.debug(u'Script result: %s', out)

        except Exception as error:
            logger.info(u'Unable to run subtitles script: %s', ex(error))

    invalidate_video_cache(video_path)