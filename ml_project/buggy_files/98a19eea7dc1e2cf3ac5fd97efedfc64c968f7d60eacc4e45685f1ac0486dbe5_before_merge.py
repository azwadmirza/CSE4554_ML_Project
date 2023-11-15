    def handle(self, *args, **options):

        hours = options['age']

        if hours:
            age = timezone.now() - timedelta(hours=hours)

        for translation in self.get_translations(**options):
            if not translation.repo_needs_commit():
                continue

            if not hours:
                age = timezone.now() - timedelta(
                    hours=translation.subproject.commit_pending_age
                )

            last_change = translation.last_change
            if last_change is None:
                continue
            if last_change > age:
                continue

            if int(options['verbosity']) >= 1:
                self.stdout.write('Committing {0}'.format(translation))
            with transaction.atomic():
                translation.commit_pending(None)