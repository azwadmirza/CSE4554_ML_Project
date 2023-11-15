def show_project(request, project):
    obj = get_project(request, project)
    user = request.user

    dict_langs = Language.objects.filter(
        dictionary__project=obj
    ).annotate(Count('dictionary')).order()

    last_changes = Change.objects.prefetch().order().filter(project=obj)[:10]

    language_stats = sort_unicode(
        obj.stats.get_language_stats(), lambda x: force_text(x.language.name)
    )

    # Paginate components of project.
    all_components = obj.component_set.select_related().order()
    components = prefetch_stats(get_paginator(
        request, all_components
    ))

    return render(
        request,
        'project.html',
        {
            'allow_index': True,
            'object': obj,
            'project': obj,
            'dicts': dict_langs,
            'last_changes': last_changes,
            'last_changes_url': urlencode(
                {'project': obj.slug}
            ),
            'language_stats': language_stats,
            'search_form': SearchForm(),
            'whiteboard_form': optional_form(
                WhiteboardForm, user, 'project.edit', obj
            ),
            'delete_form': optional_form(
                DeleteForm, user, 'project.edit', obj, obj=obj
            ),
            'rename_form': optional_form(
                ProjectRenameForm, user, 'project.edit', obj,
                request=request, instance=obj
            ),
            'replace_form': optional_form(ReplaceForm, user, 'unit.edit', obj),
            'bulk_state_form': optional_form(
                BulkStateForm, user, 'translation.auto', obj,
                user=user, obj=obj
            ),
            'components': components,
            'licenses': ', '.join(sorted(
                all_components.exclude(license='').values_list('license', flat=True)
            )),
        }
    )