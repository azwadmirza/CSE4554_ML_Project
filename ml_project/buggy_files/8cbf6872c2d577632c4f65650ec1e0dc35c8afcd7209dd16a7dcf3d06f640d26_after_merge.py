    def interface(self, 
                  start_signal,
                  image_set_start=1, 
                  image_set_end=None,
                  overwrite=True):
        '''Top-half thread for running an analysis.  Sets up grouping for jobs,
        deals with returned measurements, reports status periodically.

        start_signal- signal this semaphore when jobs are ready.
        image_set_start - beginning image set number to process
        image_set_end - last image set number to process
        overwrite - whether to recompute imagesets that already have data in initial_measurements.
        '''
        from javabridge import attach, detach
        posted_analysis_started = False
        acknowledged_thread_start = False
        measurements = None
        workspace = None
        attach()
        try:
            # listen for pipeline events, and pass them upstream
            self.pipeline.add_listener(lambda pipe, evt: self.post_event(evt))
            
            initial_measurements = None
            if self.output_path is None:
                # Caller wants a temporary measurements file.
                fd, filename = tempfile.mkstemp(
                    ".h5", dir=cpprefs.get_temporary_directory())
                try:
                    fd = os.fdopen(fd, "wb")
                    fd.write(self.initial_measurements_buf)
                    fd.close()
                    initial_measurements = cpmeas.Measurements(
                        filename=filename, mode="r")
                    measurements = cpmeas.Measurements(
                        image_set_start = None,
                        copy = initial_measurements,
                        mode = "a")
                finally:
                    if initial_measurements is not None:
                        initial_measurements.close()
                    os.unlink(filename)
            else:
                with open(self.output_path, "wb") as fd:
                    fd.write(self.initial_measurements_buf)
                measurements = cpmeas.Measurements(image_set_start=None,
                                                   filename=self.output_path,
                                                   mode="a")
            # The shared dicts are needed in jobserver()
            self.shared_dicts = [m.get_dictionary() for m in self.pipeline.modules()]
            workspace = cpw.Workspace(self.pipeline, None, None, None,
                                      measurements, cpimage.ImageSetList())
    
            if image_set_end is None:
                image_set_end = measurements.get_image_numbers()[-1]
            image_sets_to_process = filter(
                lambda x: x >= image_set_start and x <= image_set_end,
                measurements.get_image_numbers())

            self.post_event(AnalysisStarted())
            posted_analysis_started = True

            # reset the status of every image set that needs to be processed
            has_groups = measurements.has_groups()
            if self.pipeline.requires_aggregation():
                overwrite = True
            if has_groups and not overwrite:
                if not measurements.has_feature(cpmeas.IMAGE, self.STATUS):
                    overwrite = True
                else:
                    group_status = {}
                    for image_number in measurements.get_image_numbers():
                        group_number = measurements[
                            cpmeas.IMAGE, cpmeas.GROUP_NUMBER, image_number]
                        status = measurements[cpmeas.IMAGE, self.STATUS,
                                              image_number]
                        if status != self.STATUS_DONE:
                            group_status[group_number] = self.STATUS_UNPROCESSED
                        elif group_number not in group_status:
                            group_status[group_number] = self.STATUS_DONE
                            
            new_image_sets_to_process = []
            for image_set_number in image_sets_to_process:
                needs_reset = False
                if (overwrite or
                    (not measurements.has_measurements(
                        cpmeas.IMAGE, self.STATUS, image_set_number)) or
                    (measurements[cpmeas.IMAGE, self.STATUS, image_set_number] 
                     != self.STATUS_DONE)):
                    needs_reset = True
                elif has_groups:
                    group_number = measurements[
                        cpmeas.IMAGE, cpmeas.GROUP_NUMBER, image_set_number]
                    if group_status[group_number] != self.STATUS_DONE:
                        needs_reset = True
                if needs_reset:
                    measurements[cpmeas.IMAGE, self.STATUS, image_set_number] =\
                        self.STATUS_UNPROCESSED
                    new_image_sets_to_process.append(image_set_number)
            image_sets_to_process = new_image_sets_to_process

            # Find image groups.  These are written into measurements prior to
            # analysis.  Groups are processed as a single job.
            if has_groups or self.pipeline.requires_aggregation():
                worker_runs_post_group = True
                job_groups = {}
                for image_set_number in image_sets_to_process:
                    group_number = measurements[cpmeas.IMAGE, 
                                                cpmeas.GROUP_NUMBER, 
                                                image_set_number]
                    group_index = measurements[cpmeas.IMAGE, 
                                               cpmeas.GROUP_INDEX, 
                                               image_set_number]
                    job_groups[group_number] = job_groups.get(group_number, []) + [(group_index, image_set_number)]
                job_groups = [[isn for _, isn in sorted(job_groups[group_number])] 
                              for group_number in sorted(job_groups)]
            else:
                worker_runs_post_group = False  # prepare_group will be run in worker, but post_group is below.
                job_groups = [[image_set_number] for image_set_number in image_sets_to_process]

            # XXX - check that any constructed groups are complete, i.e.,
            # image_set_start and image_set_end shouldn't carve them up.

            if not worker_runs_post_group:
                # put the first job in the queue, then wait for the first image to
                # finish (see the check of self.finish_queue below) to post the rest.
                # This ensures that any shared data from the first imageset is
                # available to later imagesets.
                self.work_queue.put((job_groups[0], 
                                     worker_runs_post_group,
                                     True))
                waiting_for_first_imageset = True
                del job_groups[0]
            else:
                waiting_for_first_imageset = False
                for job in job_groups:
                    self.work_queue.put((job, worker_runs_post_group, False))
                job_groups = []
            start_signal.release()
            acknowledged_thread_start = True


            # We loop until every image is completed, or an outside event breaks the loop.
            while not self.cancelled:

                # gather measurements
                while not self.received_measurements_queue.empty():
                    image_numbers, buf = self.received_measurements_queue.get()
                    image_numbers = [int(i) for i in image_numbers]
                    recd_measurements = cpmeas.load_measurements_from_buffer(buf)
                    self.copy_recieved_measurements(recd_measurements, measurements, image_numbers)
                    recd_measurements.close()
                    del recd_measurements

                # check for jobs in progress
                while not self.in_process_queue.empty():
                    image_set_numbers = self.in_process_queue.get()
                    for image_set_number in image_set_numbers:
                        measurements[cpmeas.IMAGE, self.STATUS, int(image_set_number)] = self.STATUS_IN_PROCESS

                # check for finished jobs that haven't returned measurements, yet
                while not self.finished_queue.empty():
                    finished_req = self.finished_queue.get()
                    measurements[cpmeas.IMAGE, self.STATUS, int(finished_req.image_set_number)] = self.STATUS_FINISHED_WAITING
                    if waiting_for_first_imageset:
                        assert isinstance(finished_req, 
                                          ImageSetSuccessWithDictionary)
                        self.shared_dicts = finished_req.shared_dicts
                        waiting_for_first_imageset = False
                        assert len(self.shared_dicts) == len(self.pipeline.modules())
                        # if we had jobs waiting for the first image set to finish,
                        # queue them now that the shared state is available.
                        for job in job_groups:
                            self.work_queue.put((job, worker_runs_post_group, False))
                    finished_req.reply(Ack())

                # check progress and report
                counts = collections.Counter(measurements[cpmeas.IMAGE, self.STATUS, image_set_number]
                                             for image_set_number in image_sets_to_process)
                self.post_event(AnalysisProgress(counts))

                # Are we finished?
                if counts[self.STATUS_DONE] == len(image_sets_to_process):
                    last_image_number = measurements.get_image_numbers()[-1]
                    measurements.image_set_number = last_image_number
                    if not worker_runs_post_group:
                        self.pipeline.post_group(workspace, {})
                    
                    workspace = cpw.Workspace(self.pipeline,
                                              None, None, None,
                                              measurements, None, None)
                    workspace.post_run_display_handler = \
                        self.post_run_display_handler
                    self.pipeline.post_run(workspace)
                    break

                measurements.flush()
                # not done, wait for more work
                with self.interface_work_cv:
                    while (self.paused or
                           ((not self.cancelled) and
                            self.in_process_queue.empty() and
                            self.finished_queue.empty() and
                            self.received_measurements_queue.empty())):
                        self.interface_work_cv.wait()  # wait for a change of status or work to arrive
        finally:
            detach()
            # Note - the measurements file is owned by the queue consumer
            #        after this post_event.
            #
            if not acknowledged_thread_start:
                start_signal.release()
            if posted_analysis_started:
                was_cancelled = self.cancelled
                self.post_event(AnalysisFinished(measurements, was_cancelled))
            self.stop_workers()
        self.analysis_id = False  # this will cause the jobserver thread to exit