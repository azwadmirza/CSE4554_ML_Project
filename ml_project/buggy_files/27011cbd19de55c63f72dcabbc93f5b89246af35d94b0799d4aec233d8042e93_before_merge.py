def show_component(request, project, component):
    obj = get_component(request, project, component)
    user = request.user

    last_changes = Change.objects.prefetch().order().filter(component=obj)[:10]

    return render(
        request,
        'component.html',
        {
            'allow_index': True,
            'object': obj,
            'project': obj.project,
            'translations': sort_objects(
                prefetch_stats(obj.translation_set.all())
            ),
            'show_language': 1,
            'reports_form': ReportsForm(),
            'last_changes': last_changes,
            'last_changes_url': urlencode(
                {'component': obj.slug, 'project': obj.project.slug}
            ),
            'language_count': Language.objects.filter(
                translation__component=obj
            ).distinct().count(),
            'replace_form': optional_form(ReplaceForm, user, 'unit.edit', obj),
            'bulk_state_form': optional_form(
                BulkStateForm, user, 'translation.auto', obj,
                user=user, obj=obj
            ),
            'whiteboard_form': optional_form(
                WhiteboardForm, user, 'component.edit', obj
            ),
            'delete_form': optional_form(
                DeleteForm, user, 'component.edit', obj, obj=obj
            ),
            'rename_form': optional_form(
                ComponentRenameForm, user, 'component.edit', obj,
                request=request, instance=obj
            ),
            'move_form': optional_form(
                ComponentMoveForm, user, 'component.edit', obj,
                request=request, instance=obj
            ),
            'search_form': SearchForm(),
            'alerts': obj.alert_set.order_by('name'),
        }
    )