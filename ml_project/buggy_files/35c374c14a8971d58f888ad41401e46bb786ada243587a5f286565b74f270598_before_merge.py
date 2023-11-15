    def from_parts(cls, project, profile, args):
        """Instantiate a RuntimeConfig from its components.

        :param profile Profile: A parsed dbt Profile.
        :param project Project: A parsed dbt Project.
        :param args argparse.Namespace: The parsed command-line arguments.
        :returns RuntimeConfig: The new configuration.
        """
        quoting = deepcopy(
            get_relation_class_by_name(profile.credentials.type)
            .DEFAULTS['quote_policy']
        )
        quoting.update(project.quoting)
        return cls(
            project_name=project.project_name,
            version=project.version,
            project_root=project.project_root,
            source_paths=project.source_paths,
            macro_paths=project.macro_paths,
            data_paths=project.data_paths,
            test_paths=project.test_paths,
            analysis_paths=project.analysis_paths,
            docs_paths=project.docs_paths,
            target_path=project.target_path,
            clean_targets=project.clean_targets,
            log_path=project.log_path,
            modules_path=project.modules_path,
            quoting=quoting,
            models=project.models,
            on_run_start=project.on_run_start,
            on_run_end=project.on_run_end,
            archive=project.archive,
            seeds=project.seeds,
            packages=project.packages,
            profile_name=profile.profile_name,
            target_name=profile.target_name,
            send_anonymous_usage_stats=profile.send_anonymous_usage_stats,
            use_colors=profile.use_colors,
            threads=profile.threads,
            credentials=profile.credentials,
            args=args
        )