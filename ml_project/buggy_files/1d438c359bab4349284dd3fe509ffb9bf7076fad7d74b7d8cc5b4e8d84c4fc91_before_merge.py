    def _get_schedule(self,
                      include_opts=True,
                      include_pillar=True):
        '''
        Return the schedule data structure
        '''
        schedule = {}
        if include_pillar:
            pillar_schedule = self.opts.get('pillar', {}).get('schedule', {})
            if not isinstance(pillar_schedule, dict):
                raise ValueError('Schedule must be of type dict.')
            schedule.update(pillar_schedule)
        if include_opts:
            opts_schedule = self.opts.get('schedule', {})
            if not isinstance(opts_schedule, dict):
                raise ValueError('Schedule must be of type dict.')
            schedule.update(opts_schedule)

        return schedule