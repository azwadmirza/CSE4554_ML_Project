    def subtitles_download_in_pp():  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """Check for needed subtitles in the post process folder."""
        from sickbeard.tv import TVEpisode

        logger.info(u'Checking for needed subtitles in Post-Process folder')

        # Check if PP folder is set
        if not sickbeard.TV_DOWNLOAD_DIR or not os.path.isdir(sickbeard.TV_DOWNLOAD_DIR):
            logger.warning(u'You must set a valid post-process folder in "Post Processing" settings')
            return

        # Search for all wanted languages
        if not wanted_languages():
            return

        unpack_rar_files(sickbeard.TV_DOWNLOAD_DIR)

        run_post_process = False
        for root, _, files in os.walk(sickbeard.TV_DOWNLOAD_DIR, topdown=False):
            for filename in sorted(files):
                # Delete unwanted subtitles before downloading new ones
                delete_unwanted_subtitles(root, filename)

                if not isMediaFile(filename):
                    continue

                video_path = os.path.join(root, filename)
                tv_episode = TVEpisode.from_filepath(video_path)

                if not tv_episode:
                    logger.debug(u'%s cannot be parsed to an episode', filename)
                    continue

                if not tv_episode.show.subtitles:
                    logger.debug(u'Subtitle disabled for show: %s. Running post-process to PP it', filename)
                    run_post_process = True
                    continue

                # 'postpone' should not consider existing subtitles from db.
                tv_episode.subtitles = []
                downloaded_languages = download_subtitles(tv_episode, video_path=video_path,
                                                          subtitles=False, embedded_subtitles=False)

                # Don't run post processor unless at least one file has all of the needed subtitles OR
                # if user don't want to ignore embedded subtitles and wants to consider 'unknown' as wanted sub,
                # and .mkv has one.
                if not run_post_process and (
                        not needs_subtitles(downloaded_languages) or
                        processTV.has_matching_unknown_subtitles(video_path)):
                    run_post_process = True

        if run_post_process:
            logger.info(u'Starting post-process with default settings now that we found subtitles')
            processTV.processDir(sickbeard.TV_DOWNLOAD_DIR)