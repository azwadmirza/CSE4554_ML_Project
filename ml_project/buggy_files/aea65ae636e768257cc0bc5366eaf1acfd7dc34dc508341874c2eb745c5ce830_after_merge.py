    def handle(self, *args, **options):
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

                        build = Build.objects.create(
                            project=version.project,
                            version=version,
                            type='html',
                            state='triggered',
                        )

                        tasks.UpdateDocsTask().run(
                            pk=version.project_id,
                            build_pk=build.pk,
                            version_pk=version.pk,
                        )
                else:
                    p = Project.all_objects.get(slug=slug)
                    log.info('Building %s', p)
                    trigger_build(project=p, force=force)
        else:
            if version == 'all':
                log.info('Updating all versions')
                for version in Version.objects.filter(
                        active=True,
                        uploaded=False,
                ):
                    tasks.UpdateDocsTask().run(
                        pk=version.project_id,
                        force=force,
                        version_pk=version.pk,
                    )
            else:
                log.info('Updating all docs')
                for project in Project.objects.all():
                    tasks.UpdateDocsTask().run(
                        pk=project.pk,
                        force=force,
                    )