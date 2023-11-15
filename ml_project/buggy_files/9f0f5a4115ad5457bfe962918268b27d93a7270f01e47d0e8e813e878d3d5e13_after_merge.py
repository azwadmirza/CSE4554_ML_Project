    def save_surface_statsics_to_file(self,export_range,export_dir):
        """
        between in and out mark

            report: gaze distribution:
                    - total gazepoints
                    - gaze points on surface x
                    - gaze points not on any surface

            report: surface visisbility

                - total frames
                - surface x visible framecount

            surface events:
                frame_no, ts, surface "name", "id" enter/exit

            for each surface:
                fixations_on_name.csv
                gaze_on_name_id.csv
                positions_of_name_id.csv

        """
        metrics_dir = os.path.join(export_dir,'surfaces')
        section = export_range
        in_mark = export_range.start
        out_mark = export_range.stop
        logger.info("exporting metrics to {}".format(metrics_dir))
        if os.path.isdir(metrics_dir):
            logger.info("Will overwrite previous export for this section")
        else:
            try:
                os.mkdir(metrics_dir)
            except:
                logger.warning("Could not make metrics dir {}".format(metrics_dir))
                return


        with open(os.path.join(metrics_dir,'surface_visibility.csv'),'w',encoding='utf-8',newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')

            # surface visibility report
            frame_count = len(self.g_pool.timestamps[section])

            csv_writer.writerow(('frame_count',frame_count))
            csv_writer.writerow((''))
            csv_writer.writerow(('surface_name','visible_frame_count'))
            for s in self.surfaces:
                if s.cache == None:
                    logger.warning("The surface is not cached. Please wait for the cacher to collect data.")
                    return
                visible_count  = s.visible_count_in_section(section)
                csv_writer.writerow( (s.name, visible_count) )
            logger.info("Created 'surface_visibility.csv' file")


        with open(os.path.join(metrics_dir,'surface_gaze_distribution.csv'),'w',encoding='utf-8',newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')

            # gaze distribution report
            gaze_in_section = list(chain(*self.g_pool.gaze_positions_by_frame[section]))
            not_on_any_srf = set([gp['timestamp'] for gp in gaze_in_section])

            csv_writer.writerow(('total_gaze_point_count',len(gaze_in_section)))
            csv_writer.writerow((''))
            csv_writer.writerow(('surface_name','gaze_count'))

            for s in self.surfaces:
                gaze_on_srf  = s.gaze_on_srf_in_section(section)
                gaze_on_srf = set([gp['base_data']['timestamp'] for gp in gaze_on_srf])
                not_on_any_srf -= gaze_on_srf
                csv_writer.writerow( (s.name, len(gaze_on_srf)) )

            csv_writer.writerow(('not_on_any_surface', len(not_on_any_srf) ) )
            logger.info("Created 'surface_gaze_distribution.csv' file")



        with open(os.path.join(metrics_dir,'surface_events.csv'),'w',encoding='utf-8',newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',')

            # surface events report
            csv_writer.writerow(('frame_number','timestamp','surface_name','surface_uid','event_type'))

            events = []
            for s in self.surfaces:
                for enter_frame_id,exit_frame_id in s.cache.positive_ranges:
                    events.append({'frame_id':enter_frame_id,'srf_name':s.name,'srf_uid':s.uid,'event':'enter'})
                    events.append({'frame_id':exit_frame_id,'srf_name':s.name,'srf_uid':s.uid,'event':'exit'})

            events.sort(key=lambda x: x['frame_id'])
            for e in events:
                csv_writer.writerow( ( e['frame_id'],self.g_pool.timestamps[e['frame_id']],e['srf_name'],e['srf_uid'],e['event'] ) )
            logger.info("Created 'surface_events.csv' file")


        for s in self.surfaces:
            # per surface names:
            surface_name = '_'+s.name.replace('/','')+'_'+s.uid


            # save surface_positions as pickle file
            save_object(s.cache.to_list(),os.path.join(metrics_dir,'srf_positions'+surface_name))

            #save surface_positions as csv
            with open(os.path.join(metrics_dir,'srf_positons'+surface_name+'.csv'),'w',encoding='utf-8',newline='') as csvfile:
                csv_writer =csv.writer(csvfile, delimiter=',')
                csv_writer.writerow(('frame_idx','timestamp','m_to_screen','m_from_screen','detected_markers'))
                for idx,ts,ref_srf_data in zip(range(len(self.g_pool.timestamps)),self.g_pool.timestamps,s.cache):
                    if in_mark <= idx <= out_mark:
                        if ref_srf_data is not None and ref_srf_data is not False:
                            csv_writer.writerow( (idx,ts,ref_srf_data['m_to_screen'],ref_srf_data['m_from_screen'],ref_srf_data['detected_markers']) )


            # save gaze on srf as csv.
            with open(os.path.join(metrics_dir,'gaze_positions_on_surface'+surface_name+'.csv'),'w',encoding='utf-8',newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                csv_writer.writerow(('world_timestamp','world_frame_idx','gaze_timestamp','x_norm','y_norm','x_scaled','y_scaled','on_srf'))
                for idx,ts,ref_srf_data in zip(range(len(self.g_pool.timestamps)),self.g_pool.timestamps,s.cache):
                    if in_mark <= idx <= out_mark:
                        if ref_srf_data is not None and ref_srf_data is not False:
                            for gp in s.gaze_on_srf_by_frame_idx(idx,ref_srf_data['m_from_screen']):
                                csv_writer.writerow( (ts,idx,gp['base_data']['timestamp'],gp['norm_pos'][0],gp['norm_pos'][1],gp['norm_pos'][0]*s.real_world_size['x'],gp['norm_pos'][1]*s.real_world_size['y'],gp['on_srf']) )


            # save fixation on srf as csv.
            with open(os.path.join(metrics_dir,'fixations_on_surface'+surface_name+'.csv'),'w',encoding='utf-8',newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                csv_writer.writerow(('id','start_timestamp','duration','start_frame','end_frame','norm_pos_x','norm_pos_y','x_scaled','y_scaled','on_srf'))
                fixations_on_surface = []
                for idx,ref_srf_data in zip(range(len(self.g_pool.timestamps)),s.cache):
                    if in_mark <= idx <= out_mark:
                        if ref_srf_data is not None and ref_srf_data is not False:
                            for f in s.fixations_on_srf_by_frame_idx(idx,ref_srf_data['m_from_screen']):
                                fixations_on_surface.append(f)

                removed_duplicates = dict([(f['base_data']['id'],f) for f in fixations_on_surface]).values()
                for f_on_s in removed_duplicates:
                    f = f_on_s['base_data']
                    f_x,f_y = f_on_s['norm_pos']
                    f_on_srf = f_on_s['on_srf']
                    csv_writer.writerow( (f['id'],f['timestamp'],f['duration'],f['start_frame_index'],f['end_frame_index'],f_x,f_y,f_x*s.real_world_size['x'],f_y*s.real_world_size['y'],f_on_srf) )


            logger.info("Saved surface positon gaze and fixation data for '{}' with uid:'{}'".format(s.name,s.uid))

            if s.heatmap is not None:
                logger.info("Saved Heatmap as .png file.")
                cv2.imwrite(os.path.join(metrics_dir,'heatmap'+surface_name+'.png'),s.heatmap)


        logger.info("Done exporting reference surface data.")