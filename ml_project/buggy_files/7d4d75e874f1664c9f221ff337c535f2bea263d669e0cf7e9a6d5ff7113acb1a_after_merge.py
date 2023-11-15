    def queue_job( self, job_wrapper ):
        """Create job script and submit it to the DRM"""

        # prepare the job
        include_metadata = asbool( job_wrapper.job_destination.params.get( "embed_metadata_in_job", True ) )
        if not self.prepare_job( job_wrapper, include_metadata=include_metadata):
            return

        # get configured job destination
        job_destination = job_wrapper.job_destination

        # wrapper.get_id_tag() instead of job_id for compatibility with TaskWrappers.
        galaxy_id_tag = job_wrapper.get_id_tag()

        # get destination params
        query_params = submission_params(prefix="", **job_destination.params)
        container = None
        universe = query_params.get('universe', None)
        if universe and universe.strip().lower() == 'docker':
            container = self._find_container( job_wrapper )
            if container:
                # HTCondor needs the image as 'docker_image'
                query_params.update({'docker_image': container})

        galaxy_slots = query_params.get('request_cpus', None)
        if galaxy_slots:
            galaxy_slots_statement = 'GALAXY_SLOTS="%s"; export GALAXY_SLOTS_CONFIGURED="1"' % galaxy_slots
        else:
            galaxy_slots_statement = 'GALAXY_SLOTS="1"'

        # define job attributes
        cjs = CondorJobState(
            files_dir=self.app.config.cluster_files_directory,
            job_wrapper=job_wrapper
        )

        cluster_directory = self.app.config.cluster_files_directory
        cjs.user_log = os.path.join( cluster_directory, 'galaxy_%s.condor.log' % galaxy_id_tag )
        cjs.register_cleanup_file_attribute( 'user_log' )
        submit_file = os.path.join( cluster_directory, 'galaxy_%s.condor.desc' % galaxy_id_tag )
        executable = cjs.job_file

        build_submit_params = dict(
            executable=executable,
            output=cjs.output_file,
            error=cjs.error_file,
            user_log=cjs.user_log,
            query_params=query_params,
        )

        submit_file_contents = build_submit_description(**build_submit_params)
        script = self.get_job_file(
            job_wrapper,
            exit_code_path=cjs.exit_code_file,
            slots_statement=galaxy_slots_statement,
        )
        try:
            self.write_executable_script( executable, script )
        except:
            job_wrapper.fail( "failure preparing job script", exception=True )
            log.exception( "(%s) failure preparing job script" % galaxy_id_tag )
            return

        cleanup_job = job_wrapper.cleanup_job
        try:
            open(submit_file, "w").write(submit_file_contents)
        except Exception:
            if cleanup_job == "always":
                cjs.cleanup()
                # job_wrapper.fail() calls job_wrapper.cleanup()
            job_wrapper.fail( "failure preparing submit file", exception=True )
            log.exception( "(%s) failure preparing submit file" % galaxy_id_tag )
            return

        # job was deleted while we were preparing it
        if job_wrapper.get_state() == model.Job.states.DELETED:
            log.debug( "Job %s deleted by user before it entered the queue" % galaxy_id_tag )
            if cleanup_job in ("always", "onsuccess"):
                os.unlink( submit_file )
                cjs.cleanup()
                job_wrapper.cleanup()
            return

        log.debug( "(%s) submitting file %s" % ( galaxy_id_tag, executable ) )

        external_job_id, message = condor_submit(submit_file)
        if external_job_id is None:
            log.debug( "condor_submit failed for job %s: %s" % (job_wrapper.get_id_tag(), message) )
            if self.app.config.cleanup_job == "always":
                os.unlink( submit_file )
                cjs.cleanup()
            job_wrapper.fail( "condor_submit failed", exception=True )
            return

        os.unlink( submit_file )

        log.info( "(%s) queued as %s" % ( galaxy_id_tag, external_job_id ) )

        # store runner information for tracking if Galaxy restarts
        job_wrapper.set_job_destination( job_destination, external_job_id )

        # Store DRM related state information for job
        cjs.job_id = external_job_id
        cjs.job_destination = job_destination

        # Add to our 'queue' of jobs to monitor
        self.monitor_queue.put( cjs )