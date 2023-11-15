    def handle(self, *args, **options):
        record = options['record']
        force = options['force']
        version = options['version']

        if options.get('slugs', []):
            for slug in options['slugs']:
                if version and version != 'all':
                    log.info('Updating version %s for %s', version, slug)
                    for version in Version.objects.filter(
                            project__slug=slug,
                            slug=version,
                    ):
                        trigger_build(project=version.project, version=version)
                elif version == 'all':
                    log.info('Updating all versions for %s', slug)
                    for version in Version.objects.filter(
                            project__slug=slug,
                            active=True,
                            uploaded=False,
                    ):

                        build_pk = None
                        if record:
                            build = Build.objects.create(
                                project=version.project,
                                version=version,
                                type='html',
                                state='triggered',
                            )
                            build_pk = build.pk

                        tasks.UpdateDocsTask().run(
                            pk=version.project_id,
                            build_pk=build_pk,
                            record=record,
                            version_pk=version.pk,
                        )
                else:
                    p = Project.all_objects.get(slug=slug)
                    log.info('Building %s', p)
                    trigger_build(project=p, force=force, record=record)
        else:
            if version == 'all':
                log.info('Updating all versions')
                for version in Version.objects.filter(
                        active=True,
                        uploaded=False,
                ):
                    tasks.UpdateDocsTask().run(
                        pk=version.project_id,
                        record=record,
                        force=force,
                        version_pk=version.pk,
                    )
            else:
                log.info('Updating all docs')
                for project in Project.objects.all():
                    tasks.UpdateDocsTask().run(
                        pk=project.pk,
                        record=record,
                        force=force,
                    )