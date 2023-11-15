    def subtitles_download_in_pp():  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """Check for needed subtitles in the post process folder."""
        from . import process_tv
        from .tv import Episode

        logger.info(u'Checking for needed subtitles in Post-Process folder')

        # Check if PP folder is set
        if not app.TV_DOWNLOAD_DIR or not os.path.isdir(app.TV_DOWNLOAD_DIR):
            logger.warning(u'You must set a valid post-process folder in "Post Processing" settings')
            return

        # Search for all wanted languages
        if not wanted_languages():
            return

        SubtitlesFinder.unpack_rar_files(app.TV_DOWNLOAD_DIR)

        run_post_process = False
        for root, _, files in os.walk(app.TV_DOWNLOAD_DIR, topdown=False):
            # Skip folders that are being used for unpacking
            if u'_UNPACK' in root.upper():
                continue
            for filename in sorted(files):
                # Delete unwanted subtitles before downloading new ones
                delete_unwanted_subtitles(root, filename)

                if not is_media_file(filename):
                    continue

                video_path = os.path.join(root, filename)
                tv_episode = Episode.from_filepath(video_path)

                if not tv_episode:
                    logger.debug(u'%s cannot be parsed to an episode', filename)
                    continue

                if tv_episode.status not in Quality.SNATCHED + Quality.SNATCHED_PROPER + Quality.SNATCHED_BEST:
                    continue

                if not tv_episode.show.subtitles:
                    logger.debug(u'Subtitle disabled for show: %s. Running post-process to PP it', filename)
                    run_post_process = True
                    continue

                # Should not consider existing subtitles from db if it's a replacement
                new_release_name = remove_extension(filename)
                if tv_episode.release_name and new_release_name != tv_episode.release_name:
                    logger.debug(u"As this is a release replacement I'm not going to consider existing "
                                 u"subtitles or release name from database to refine the new release")
                    logger.debug(u"Replacing old release name '%s' with new release name '%s'",
                                 tv_episode.release_name, new_release_name)
                    tv_episode.subtitles = []
                    tv_episode.release_name = new_release_name
                embedded_subtitles = bool(not app.IGNORE_EMBEDDED_SUBS and video_path.endswith('.mkv'))
                downloaded_languages = download_subtitles(tv_episode, video_path=video_path,
                                                          subtitles=False, embedded_subtitles=embedded_subtitles)

                # Don't run post processor unless at least one file has all of the needed subtitles OR
                # if user don't want to ignore embedded subtitles and wants to consider 'unknown' as wanted sub,
                # and .mkv has one.
                if not app.PROCESS_AUTOMATICALLY and not run_post_process:
                    if not needs_subtitles(downloaded_languages):
                        run_post_process = True
                    elif not app.IGNORE_EMBEDDED_SUBS:
                        embedded_subs = get_embedded_subtitles(video_path)
                        run_post_process = accept_unknown(embedded_subs) or accept_any(embedded_subs)

        if run_post_process:
            logger.info(u'Starting post-process with default settings now that we found subtitles')
            process_tv.ProcessResult(app.TV_DOWNLOAD_DIR, app.PROCESS_METHOD).process()