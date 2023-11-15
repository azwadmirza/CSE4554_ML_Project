def run_subs_scripts(video_path, scripts, script_args):
    """Execute subtitle scripts

    :param video_path: the video path
    :type video_path: str
    :param scripts: the script commands to be executed
    :type scripts: list of str
    :param script_args: the arguments to be passed to the script
    :type script_args: list of str
    """
    for script_name in scripts:
        script_cmd = [piece for piece in re.split("( |\\\".*?\\\"|'.*?')", script_name) if piece.strip()]

        logger.info(u'Running subtitle %s-script: %s', 'extra' if len(script_args) > 1 else 'pre', script_name)
        inner_cmd = script_cmd + script_args

        # use subprocess to run the command and capture output
        logger.info(u'Executing command: %s', inner_cmd)
        try:
            process = subprocess.Popen(inner_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, cwd=sickbeard.PROG_DIR)
            out, _ = process.communicate()  # @UnusedVariable
            logger.debug(u'Script result: %s', out)

        except Exception as error:
            logger.info(u'Unable to run subtitles script: %s', ex(error))

    invalidate_video_cache(video_path)