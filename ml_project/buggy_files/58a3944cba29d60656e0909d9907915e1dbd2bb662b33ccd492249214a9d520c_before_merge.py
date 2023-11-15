    def subtitles_download_in_pp():  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """Checks for needed subtitles in the post process folder.
        """
        logger.info(u'Checking for needed subtitles in Post-Process folder')

        # Check if PP folder is set
        if not sickbeard.TV_DOWNLOAD_DIR or not os.path.isdir(sickbeard.TV_DOWNLOAD_DIR):
            logger.warning(u'You must set a valid post-process folder in "Post Processing" settings')
            return

        # Search for all wanted languages
        languages = {from_code(language) for language in wanted_languages()}
        if not languages:
            return

        unpack_rar_files(sickbeard.TV_DOWNLOAD_DIR)

        pool = get_provider_pool()
        run_post_process = False
        for root, _, files in os.walk(sickbeard.TV_DOWNLOAD_DIR, topdown=False):
            for filename in sorted(files):
                filename = clear_non_release_groups(filename)

                # Delete unwanted subtitles before downloading new ones
                delete_unwanted_subtitles(root, filename)

                if not isMediaFile(filename):
                    continue

                if processTV.subtitles_enabled(filename) is False:
                    logger.debug(u'Subtitle disabled for show: %s', filename)
                    continue

                video_path = os.path.join(root, filename)
                release_name = os.path.splitext(filename)[0]
                found_subtitles = download_best_subs(video_path, root, release_name, languages, subtitles=False,
                                                     embedded_subtitles=False, provider_pool=pool)
                downloaded_languages = {s.language.opensubtitles for s in found_subtitles}

                # Don't run post processor unless at least one file has all of the needed subtitles
                if not run_post_process and not needs_subtitles(downloaded_languages):
                    run_post_process = True

        if run_post_process:
            logger.info(u'Starting post-process with default settings now that we found subtitles')
            processTV.processDir(sickbeard.TV_DOWNLOAD_DIR)