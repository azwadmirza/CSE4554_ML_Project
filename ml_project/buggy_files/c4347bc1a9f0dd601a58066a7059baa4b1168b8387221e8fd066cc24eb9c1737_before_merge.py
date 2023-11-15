    def handle(self, *args, **options):
        """Automatic import of components."""
        # Get project
        try:
            project = Project.objects.get(slug=options['project'])
        except Project.DoesNotExist:
            raise CommandError('Project does not exist!')

        # Get main component
        main_component = None
        if options['main_component']:
            try:
                main_component = Component.objects.get(
                    project=project,
                    slug=options['main_component']
                )
            except Component.DoesNotExist:
                raise CommandError('Main component does not exist!')

        try:
            data = json.load(options['json-file'])
        except ValueError:
            raise CommandError('Failed to parse JSON file!')
        finally:
            options['json-file'].close()

        for item in data:
            if ('filemask' not in item or
                    'name' not in item):
                raise CommandError('Missing required fields in JSON!')

            if 'slug' not in item:
                item['slug'] = slugify(item['name'])

            if 'repo' not in item:
                if main_component is None:
                    raise CommandError(
                        'No main component and no repository URL!'
                    )
                item['repo'] = main_component.get_repo_link_url()

            item['project'] = project

            try:
                component = Component.objects.get(
                    slug=item['slug'], project=item['project']
                )
                self.stderr.write(
                    'Component {0} already exists'.format(component)
                )
                if options['ignore']:
                    continue
                if options['update']:
                    for key in item:
                        if key in ('project', 'slug'):
                            continue
                        setattr(component, key, item[key])
                    component.save()
                    continue
                raise CommandError(
                    'Component already exists, use --ignore or --update!'
                )

            except Component.DoesNotExist:
                component = Component.objects.create(**item)
                self.stdout.write(
                    'Imported {0} with {1} translations'.format(
                        component,
                        component.translation_set.count()
                    )
                )