    def massEditSubmit(self, paused=None, default_ep_status=None, dvd_order=None,
                       anime=None, sports=None, scene=None, flatten_folders=None, quality_preset=None,
                       subtitles=None, air_by_date=None, allowed_qualities=None, preferred_qualities=None, toEdit=None, *args,
                       **kwargs):
        allowed_qualities = allowed_qualities or []
        preferred_qualities = preferred_qualities or []

        dir_map = {}
        for cur_arg in kwargs:
            if not cur_arg.startswith('orig_root_dir_'):
                continue
            which_index = cur_arg.replace('orig_root_dir_', '')
            end_dir = kwargs['new_root_dir_{index}'.format(index=which_index)]
            dir_map[kwargs[cur_arg]] = end_dir

        show_ids = toEdit.split('|') if toEdit else []
        errors = 0
        for cur_show in show_ids:
            show_obj = Show.find(app.showList, int(cur_show))
            if not show_obj:
                continue

            cur_root_dir = os.path.dirname(show_obj._location)
            cur_show_dir = os.path.basename(show_obj._location)
            if cur_root_dir in dir_map and cur_root_dir != dir_map[cur_root_dir]:
                new_show_dir = os.path.join(dir_map[cur_root_dir], cur_show_dir)
                logger.log(u'For show {show.name} changing dir from {show._location} to {location}'.format
                           (show=show_obj, location=new_show_dir))
            else:
                new_show_dir = show_obj._location

            if paused == 'keep':
                new_paused = show_obj.paused
            else:
                new_paused = True if paused == 'enable' else False
            new_paused = 'on' if new_paused else 'off'

            if default_ep_status == 'keep':
                new_default_ep_status = show_obj.default_ep_status
            else:
                new_default_ep_status = default_ep_status

            if anime == 'keep':
                new_anime = show_obj.anime
            else:
                new_anime = True if anime == 'enable' else False
            new_anime = 'on' if new_anime else 'off'

            if sports == 'keep':
                new_sports = show_obj.sports
            else:
                new_sports = True if sports == 'enable' else False
            new_sports = 'on' if new_sports else 'off'

            if scene == 'keep':
                new_scene = show_obj.is_scene
            else:
                new_scene = True if scene == 'enable' else False
            new_scene = 'on' if new_scene else 'off'

            if air_by_date == 'keep':
                new_air_by_date = show_obj.air_by_date
            else:
                new_air_by_date = True if air_by_date == 'enable' else False
            new_air_by_date = 'on' if new_air_by_date else 'off'

            if dvd_order == 'keep':
                new_dvd_order = show_obj.dvd_order
            else:
                new_dvd_order = True if dvd_order == 'enable' else False
            new_dvd_order = 'on' if new_dvd_order else 'off'

            if flatten_folders == 'keep':
                new_flatten_folders = show_obj.flatten_folders
            else:
                new_flatten_folders = True if flatten_folders == 'enable' else False
            new_flatten_folders = 'on' if new_flatten_folders else 'off'

            if subtitles == 'keep':
                new_subtitles = show_obj.subtitles
            else:
                new_subtitles = True if subtitles == 'enable' else False

            new_subtitles = 'on' if new_subtitles else 'off'

            if quality_preset == 'keep':
                allowed_qualities, preferred_qualities = show_obj.current_qualities
            elif try_int(quality_preset, None):
                preferred_qualities = []

            exceptions_list = []

            errors += self.editShow(cur_show, new_show_dir, allowed_qualities,
                                    preferred_qualities, exceptions_list,
                                    defaultEpStatus=new_default_ep_status,
                                    flatten_folders=new_flatten_folders,
                                    paused=new_paused, sports=new_sports, dvd_order=new_dvd_order,
                                    subtitles=new_subtitles, anime=new_anime,
                                    scene=new_scene, air_by_date=new_air_by_date,
                                    directCall=True)

        if errors:
            ui.notifications.error('Errors', '{num} error{s} while saving changes. Please check logs'.format
                                   (num=errors, s='s' if errors > 1 else ''))

        return self.redirect('/manage/')