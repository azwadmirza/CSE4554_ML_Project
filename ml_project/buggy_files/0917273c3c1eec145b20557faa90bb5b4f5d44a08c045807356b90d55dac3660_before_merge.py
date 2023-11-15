    def subtitleMissedPP(self):
        t = PageTemplate(rh=self, filename='manage_subtitleMissedPP.mako')
        app.RELEASES_IN_PP = []
        for root, _, files in os.walk(app.TV_DOWNLOAD_DIR, topdown=False):
            for filename in sorted(files):
                if not isMediaFile(filename):
                    continue

                video_path = os.path.join(root, filename)
                video_date = datetime.datetime.fromtimestamp(os.stat(video_path).st_ctime)
                video_age = datetime.datetime.today() - video_date

                tv_episode = TVEpisode.from_filepath(video_path)

                if not tv_episode:
                    logger.debug(u'%s cannot be parsed to an episode', filename)
                    continue

                if not tv_episode.show.subtitles:
                    continue

                related_files = postProcessor.PostProcessor(video_path).list_associated_files(video_path, base_name_only=True, subfolders=False)
                if related_files:
                    continue

                age_hours = divmod(video_age.seconds, 3600)[0]
                age_minutes = divmod(video_age.seconds, 60)[0]
                if video_age.days > 0:
                    age_unit = 'd'
                    age_value = video_age.days
                elif age_hours > 0:
                    age_unit = 'h'
                    age_value = age_hours
                else:
                    age_unit = 'm'
                    age_value = age_minutes

                app.RELEASES_IN_PP.append({'release': video_path, 'show': tv_episode.show.indexerid, 'show_name': tv_episode.show.name,
                                           'season': tv_episode.season, 'episode': tv_episode.episode,
                                           'age': age_value, 'age_unit': age_unit, 'age_raw': video_age})
        app.RELEASES_IN_PP = sorted(app.RELEASES_IN_PP, key=lambda k: k['age_raw'], reverse=True)

        return t.render(releases_in_pp=app.RELEASES_IN_PP, title='Missing Subtitles in Post-Process folder',
                        header='Missing Subtitles in Post Process folder', topmenu='manage',
                        controller='manage', action='subtitleMissedPP')