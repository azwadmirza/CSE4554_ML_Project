    def execute(
        self,
        targets=None,
        dryrun=False,
        touch=False,
        local_cores=1,
        forcetargets=False,
        forceall=False,
        forcerun=None,
        until=[],
        omit_from=[],
        prioritytargets=None,
        quiet=False,
        keepgoing=False,
        printshellcmds=False,
        printreason=False,
        printdag=False,
        cluster=None,
        cluster_sync=None,
        jobname=None,
        immediate_submit=False,
        ignore_ambiguity=False,
        printrulegraph=False,
        printfilegraph=False,
        printd3dag=False,
        drmaa=None,
        drmaa_log_dir=None,
        kubernetes=None,
        tibanna=None,
        tibanna_sfn=None,
        precommand="",
        container_image=None,
        stats=None,
        force_incomplete=False,
        ignore_incomplete=False,
        list_version_changes=False,
        list_code_changes=False,
        list_input_changes=False,
        list_params_changes=False,
        list_untracked=False,
        list_conda_envs=False,
        summary=False,
        archive=None,
        delete_all_output=False,
        delete_temp_output=False,
        detailed_summary=False,
        latency_wait=3,
        wait_for_files=None,
        nolock=False,
        unlock=False,
        notemp=False,
        nodeps=False,
        cleanup_metadata=None,
        cleanup_conda=False,
        cleanup_shadow=False,
        cleanup_scripts=True,
        subsnakemake=None,
        updated_files=None,
        keep_target_files=False,
        keep_shadow=False,
        keep_remote_local=False,
        allowed_rules=None,
        max_jobs_per_second=None,
        max_status_checks_per_second=None,
        greediness=1.0,
        no_hooks=False,
        force_use_threads=False,
        create_envs_only=False,
        assume_shared_fs=True,
        cluster_status=None,
        report=None,
        export_cwl=False,
        batch=None,
        keepincomplete=False,
    ):

        self.check_localrules()
        self.immediate_submit = immediate_submit
        self.cleanup_scripts = cleanup_scripts

        def rules(items):
            return map(self._rules.__getitem__, filter(self.is_rule, items))

        if keep_target_files:

            def files(items):
                return filterfalse(self.is_rule, items)

        else:

            def files(items):
                relpath = lambda f: f if os.path.isabs(f) else os.path.relpath(f)
                return map(relpath, filterfalse(self.is_rule, items))

        if not targets:
            targets = [self.first_rule] if self.first_rule is not None else list()

        if prioritytargets is None:
            prioritytargets = list()
        if forcerun is None:
            forcerun = list()
        if until is None:
            until = list()
        if omit_from is None:
            omit_from = list()

        priorityrules = set(rules(prioritytargets))
        priorityfiles = set(files(prioritytargets))
        forcerules = set(rules(forcerun))
        forcefiles = set(files(forcerun))
        untilrules = set(rules(until))
        untilfiles = set(files(until))
        omitrules = set(rules(omit_from))
        omitfiles = set(files(omit_from))
        targetrules = set(
            chain(
                rules(targets),
                filterfalse(Rule.has_wildcards, priorityrules),
                filterfalse(Rule.has_wildcards, forcerules),
                filterfalse(Rule.has_wildcards, untilrules),
            )
        )
        targetfiles = set(chain(files(targets), priorityfiles, forcefiles, untilfiles))
        if forcetargets:
            forcefiles.update(targetfiles)
            forcerules.update(targetrules)

        rules = self.rules
        if allowed_rules:
            rules = [rule for rule in rules if rule.name in set(allowed_rules)]

        if wait_for_files is not None:
            try:
                snakemake.io.wait_for_files(wait_for_files, latency_wait=latency_wait)
            except IOError as e:
                logger.error(str(e))
                return False

        dag = DAG(
            self,
            rules,
            dryrun=dryrun,
            targetfiles=targetfiles,
            targetrules=targetrules,
            # when cleaning up conda, we should enforce all possible jobs
            # since their envs shall not be deleted
            forceall=forceall or cleanup_conda,
            forcefiles=forcefiles,
            forcerules=forcerules,
            priorityfiles=priorityfiles,
            priorityrules=priorityrules,
            untilfiles=untilfiles,
            untilrules=untilrules,
            omitfiles=omitfiles,
            omitrules=omitrules,
            ignore_ambiguity=ignore_ambiguity,
            force_incomplete=force_incomplete,
            ignore_incomplete=ignore_incomplete
            or printdag
            or printrulegraph
            or printfilegraph,
            notemp=notemp,
            keep_remote_local=keep_remote_local,
            batch=batch,
        )

        self.persistence = Persistence(
            nolock=nolock,
            dag=dag,
            conda_prefix=self.conda_prefix,
            singularity_prefix=self.singularity_prefix,
            shadow_prefix=self.shadow_prefix,
            warn_only=dryrun
            or printrulegraph
            or printfilegraph
            or printdag
            or summary
            or archive
            or list_version_changes
            or list_code_changes
            or list_input_changes
            or list_params_changes
            or list_untracked
            or delete_all_output
            or delete_temp_output,
        )

        if cleanup_metadata:
            for f in cleanup_metadata:
                self.persistence.cleanup_metadata(f)
            return True

        logger.info("Building DAG of jobs...")
        dag.init()
        dag.update_checkpoint_dependencies()
        # check incomplete has to run BEFORE any call to postprocess
        dag.check_incomplete()
        dag.check_dynamic()

        if unlock:
            try:
                self.persistence.cleanup_locks()
                logger.info("Unlocking working directory.")
                return True
            except IOError:
                logger.error(
                    "Error: Unlocking the directory {} failed. Maybe "
                    "you don't have the permissions?"
                )
                return False
        try:
            self.persistence.lock()
        except IOError:
            logger.error(
                "Error: Directory cannot be locked. Please make "
                "sure that no other Snakemake process is trying to create "
                "the same files in the following directory:\n{}\n"
                "If you are sure that no other "
                "instances of snakemake are running on this directory, "
                "the remaining lock was likely caused by a kill signal or "
                "a power loss. It can be removed with "
                "the --unlock argument.".format(os.getcwd())
            )
            return False

        if cleanup_shadow:
            self.persistence.cleanup_shadow()
            return True

        if (
            self.subworkflows
            and not printdag
            and not printrulegraph
            and not printfilegraph
        ):
            # backup globals
            globals_backup = dict(self.globals)
            # execute subworkflows
            for subworkflow in self.subworkflows:
                subworkflow_targets = subworkflow.targets(dag)
                logger.debug(
                    "Files requested from subworkflow:\n    {}".format(
                        "\n    ".join(subworkflow_targets)
                    )
                )
                updated = list()
                if subworkflow_targets:
                    logger.info("Executing subworkflow {}.".format(subworkflow.name))
                    if not subsnakemake(
                        subworkflow.snakefile,
                        workdir=subworkflow.workdir,
                        targets=subworkflow_targets,
                        configfiles=[subworkflow.configfile],
                        updated_files=updated,
                    ):
                        return False
                    dag.updated_subworkflow_files.update(
                        subworkflow.target(f) for f in updated
                    )
                else:
                    logger.info(
                        "Subworkflow {}: Nothing to be done.".format(subworkflow.name)
                    )
            if self.subworkflows:
                logger.info("Executing main workflow.")
            # rescue globals
            self.globals.update(globals_backup)

        dag.postprocess()
        # deactivate IOCache such that from now on we always get updated
        # size, existence and mtime information
        # ATTENTION: this may never be removed without really good reason.
        # Otherwise weird things may happen.
        self.iocache.deactivate()
        # clear and deactivate persistence cache, from now on we want to see updates
        self.persistence.deactivate_cache()

        if nodeps:
            missing_input = [
                f
                for job in dag.targetjobs
                for f in job.input
                if dag.needrun(job) and not os.path.exists(f)
            ]
            if missing_input:
                logger.error(
                    "Dependency resolution disabled (--nodeps) "
                    "but missing input "
                    "files detected. If this happens on a cluster, please make sure "
                    "that you handle the dependencies yourself or turn off "
                    "--immediate-submit. Missing input files:\n{}".format(
                        "\n".join(missing_input)
                    )
                )
                return False

        updated_files.extend(f for job in dag.needrun_jobs for f in job.output)

        if export_cwl:
            from snakemake.cwl import dag_to_cwl
            import json

            with open(export_cwl, "w") as cwl:
                json.dump(dag_to_cwl(dag), cwl, indent=4)
            return True
        elif report:
            from snakemake.report import auto_report

            auto_report(dag, report)
            return True
        elif printd3dag:
            dag.d3dag()
            return True
        elif printdag:
            print(dag)
            return True
        elif printrulegraph:
            print(dag.rule_dot())
            return True
        elif printfilegraph:
            print(dag.filegraph_dot())
            return True
        elif summary:
            print("\n".join(dag.summary(detailed=False)))
            return True
        elif detailed_summary:
            print("\n".join(dag.summary(detailed=True)))
            return True
        elif archive:
            dag.archive(archive)
            return True
        elif delete_all_output:
            dag.clean(only_temp=False, dryrun=dryrun)
            return True
        elif delete_temp_output:
            dag.clean(only_temp=True, dryrun=dryrun)
            return True
        elif list_version_changes:
            items = list(chain(*map(self.persistence.version_changed, dag.jobs)))
            if items:
                print(*items, sep="\n")
            return True
        elif list_code_changes:
            items = list(chain(*map(self.persistence.code_changed, dag.jobs)))
            for j in dag.jobs:
                items.extend(list(j.outputs_older_than_script_or_notebook()))
            if items:
                print(*items, sep="\n")
            return True
        elif list_input_changes:
            items = list(chain(*map(self.persistence.input_changed, dag.jobs)))
            if items:
                print(*items, sep="\n")
            return True
        elif list_params_changes:
            items = list(chain(*map(self.persistence.params_changed, dag.jobs)))
            if items:
                print(*items, sep="\n")
            return True
        elif list_untracked:
            dag.list_untracked()
            return True

        if self.use_singularity:
            if assume_shared_fs:
                dag.pull_container_imgs(
                    dryrun=dryrun or list_conda_envs, quiet=list_conda_envs
                )
        if self.use_conda:
            if assume_shared_fs:
                dag.create_conda_envs(
                    dryrun=dryrun or list_conda_envs or cleanup_conda,
                    quiet=list_conda_envs,
                )
            if create_envs_only:
                return True

        if list_conda_envs:
            print("environment", "container", "location", sep="\t")
            for env in set(job.conda_env for job in dag.jobs):
                if env:
                    print(
                        simplify_path(env.file),
                        env.container_img_url or "",
                        simplify_path(env.path),
                        sep="\t",
                    )
            return True

        if cleanup_conda:
            self.persistence.cleanup_conda()
            return True

        scheduler = JobScheduler(
            self,
            dag,
            self.cores,
            local_cores=local_cores,
            dryrun=dryrun,
            touch=touch,
            cluster=cluster,
            cluster_status=cluster_status,
            cluster_config=cluster_config,
            cluster_sync=cluster_sync,
            jobname=jobname,
            max_jobs_per_second=max_jobs_per_second,
            max_status_checks_per_second=max_status_checks_per_second,
            quiet=quiet,
            keepgoing=keepgoing,
            drmaa=drmaa,
            drmaa_log_dir=drmaa_log_dir,
            kubernetes=kubernetes,
            tibanna=tibanna,
            tibanna_sfn=tibanna_sfn,
            precommand=precommand,
            container_image=container_image,
            printreason=printreason,
            printshellcmds=printshellcmds,
            latency_wait=latency_wait,
            greediness=greediness,
            force_use_threads=force_use_threads,
            assume_shared_fs=assume_shared_fs,
            keepincomplete=keepincomplete,
        )

        if not dryrun:
            if len(dag):
                shell_exec = shell.get_executable()
                if shell_exec is not None:
                    logger.info("Using shell: {}".format(shell_exec))
                if cluster or cluster_sync or drmaa:
                    logger.resources_info(
                        "Provided cluster nodes: {}".format(self.nodes)
                    )
                else:
                    warning = (
                        "" if self.cores > 1 else " (use --cores to define parallelism)"
                    )
                    logger.resources_info(
                        "Provided cores: {}{}".format(self.cores, warning)
                    )
                    logger.resources_info(
                        "Rules claiming more threads " "will be scaled down."
                    )

                provided_resources = format_resources(self.global_resources)
                if provided_resources:
                    logger.resources_info("Provided resources: " + provided_resources)

                if self.run_local and any(rule.group for rule in self.rules):
                    logger.info("Group jobs: inactive (local execution)")

                if not self.use_conda and any(rule.conda_env for rule in self.rules):
                    logger.info("Conda environments: ignored")

                if not self.use_singularity and any(
                    rule.container_img for rule in self.rules
                ):
                    logger.info("Singularity containers: ignored")

                logger.run_info("\n".join(dag.stats()))
            else:
                logger.info("Nothing to be done.")
        else:
            # the dryrun case
            if len(dag):
                logger.run_info("\n".join(dag.stats()))
            else:
                logger.info("Nothing to be done.")
                return True
            if quiet:
                # in case of dryrun and quiet, just print above info and exit
                return True

        if not dryrun and not no_hooks:
            self._onstart(logger.get_logfile())

        success = scheduler.schedule()

        if success:
            if dryrun:
                if len(dag):
                    logger.run_info("\n".join(dag.stats()))
                logger.info(
                    "This was a dry-run (flag -n). The order of jobs "
                    "does not reflect the order of execution."
                )
                logger.remove_logfile()
            else:
                if stats:
                    scheduler.stats.to_json(stats)
                logger.logfile_hint()
            if not dryrun and not no_hooks:
                self._onsuccess(logger.get_logfile())
            return True
        else:
            if not dryrun and not no_hooks:
                self._onerror(logger.get_logfile())
            logger.logfile_hint()
            return False