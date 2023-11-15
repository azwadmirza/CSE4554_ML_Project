    def handle(self, *args, **options):
        current_page_id = None
        missing_models_content_type_ids = set()
        for revision in PageRevision.objects.order_by('page_id', 'created_at').select_related('page').iterator():
            # This revision is for a page type that is no longer in the database. Bail out early.
            if revision.page.content_type_id in missing_models_content_type_ids:
                continue
            if not revision.page.specific_class:
                missing_models_content_type_ids.add(revision.page.content_type_id)
                continue

            is_new_page = revision.page_id != current_page_id
            if is_new_page:
                # reset previous revision when encountering a new page.
                previous_revision = None

            has_content_changes = False
            current_page_id = revision.page_id

            if not PageLogEntry.objects.filter(revision=revision).exists():
                current_revision_as_page = revision.as_page_object()
                published = revision.id == revision.page.live_revision_id

                if previous_revision is not None:
                    # Must use .specific so the comparison picks up all fields, not just base Page ones.
                    comparison = get_comparison(revision.page.specific, previous_revision.as_page_object(), current_revision_as_page)
                    has_content_changes = len(comparison) > 0

                    if current_revision_as_page.live_revision_id == previous_revision.id:
                        # Log the previous revision publishing.
                        self.log_page_action('wagtail.publish', previous_revision, True)

                if is_new_page or has_content_changes or published:
                    if is_new_page:
                        action = 'wagtail.create'
                    elif published:
                        action = 'wagtail.publish'
                    else:
                        action = 'wagtail.edit'

                    if published and has_content_changes:
                        # When publishing, also log the 'draft save', but only if there have been content changes
                        self.log_page_action('wagtail.edit', revision, has_content_changes)

                    self.log_page_action(action, revision, has_content_changes)

            previous_revision = revision