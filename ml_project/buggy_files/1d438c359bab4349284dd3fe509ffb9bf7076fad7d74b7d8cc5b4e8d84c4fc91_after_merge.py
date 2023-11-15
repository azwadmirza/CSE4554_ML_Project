    def _get_schedule(self,
                      include_opts=True,
                      include_pillar=True,
                      remove_hidden=False):
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

        if remove_hidden:
            _schedule = copy.deepcopy(schedule)
            for job in _schedule:
                for item in _schedule[job]:
                    if item.startswith('_'):
                        del schedule[job][item]
        return schedule