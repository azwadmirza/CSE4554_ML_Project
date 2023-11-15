def preview_on_create(request, content_type_app_name, content_type_model_name, parent_page_id):
    # Receive the form submission that would typically be posted to the 'create' view. If submission is valid,
    # return the rendered page; if not, re-render the edit form
    try:
        content_type = ContentType.objects.get_by_natural_key(content_type_app_name, content_type_model_name)
    except ContentType.DoesNotExist:
        raise Http404

    page_class = content_type.model_class()
    page = page_class()
    edit_handler_class = page_class.get_edit_handler()
    form_class = edit_handler_class.get_form_class(page_class)
    parent_page = get_object_or_404(Page, id=parent_page_id).specific

    form = form_class(request.POST, request.FILES, instance=page, parent_page=parent_page)

    if form.is_valid():
        form.save(commit=False)

        # We need to populate treebeard's path / depth fields in order to pass validation.
        # We can't make these 100% consistent with the rest of the tree without making actual
        # database changes (such as incrementing the parent's numchild field), but by
        # calling treebeard's internal _get_path method, we can set a 'realistic' value that
        # will hopefully enable tree traversal operations to at least partially work.
        page.depth = parent_page.depth + 1

        if parent_page.is_leaf():
            # set the path as the first child of parent_page
            page.path = page._get_path(parent_page.path, page.depth, 1)
        else:
            # add the new page after the last child of parent_page
            page.path = parent_page.get_last_child()._inc_path()

        # ensure that our unsaved page instance has a suitable url set
        page.set_url_path(parent_page)

        page.full_clean()

        # Set treebeard attributes
        page.depth = parent_page.depth + 1
        page.path = Page._get_children_path_interval(parent_page.path)[1]

        preview_mode = request.GET.get('mode', page.default_preview_mode)
        response = page.serve_preview(page.dummy_request(), preview_mode)
        response['X-Wagtail-Preview'] = 'ok'
        return response

    else:
        edit_handler = edit_handler_class(instance=page, form=form)

        response = render(request, 'wagtailadmin/pages/create.html', {
            'content_type': content_type,
            'page_class': page_class,
            'parent_page': parent_page,
            'edit_handler': edit_handler,
            'preview_modes': page.preview_modes,
            'form': form,
        })
        response['X-Wagtail-Preview'] = 'error'
        return response