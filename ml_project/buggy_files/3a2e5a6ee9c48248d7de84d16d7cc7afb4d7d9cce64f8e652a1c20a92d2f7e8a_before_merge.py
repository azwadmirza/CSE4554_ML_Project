    def combine_info(self, all_infos):
        """Combine metadata for multiple datasets.

        When loading data from multiple files it can be non-trivial to combine
        things like start_time, end_time, start_orbit, end_orbit, etc.

        By default this method will produce a dictionary containing all values
        that were equal across **all** provided info dictionaries.

        Additionally it performs the logical comparisons to produce the
        following if they exist:

         - start_time
         - end_time
         - start_orbit
         - end_orbit

         Also, concatenate the areas.

        """
        combined_info = combine_info(*all_infos)
        if 'start_time' not in combined_info and 'start_time' in all_infos[0]:
            combined_info['start_time'] = min(
                i['start_time'] for i in all_infos)
        if 'end_time' not in combined_info and 'end_time' in all_infos[0]:
            combined_info['end_time'] = max(i['end_time'] for i in all_infos)
        if 'start_orbit' not in combined_info and 'start_orbit' in all_infos[0]:
            combined_info['start_orbit'] = min(
                i['start_orbit'] for i in all_infos)
        if 'end_orbit' not in combined_info and 'end_orbit' in all_infos[0]:
            combined_info['end_orbit'] = max(i['end_orbit'] for i in all_infos)

        try:
            area = SwathDefinition(lons=np.ma.vstack([info['area'].lons for info in all_infos]),
                                   lats=np.ma.vstack([info['area'].lats for info in all_infos]))
            area.name = '_'.join([info['area'].name for info in all_infos])
            combined_info['area'] = area
        except KeyError:
            pass

        return combined_info