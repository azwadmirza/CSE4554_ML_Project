    def save_model(self, request, obj, form, change):
        """
        Move the page in the tree if necessary and save every placeholder
        Content object.
        """
        target = request.GET.get('target', None)
        position = request.GET.get('position', None)

        if 'recover' in request.path_info:
            pk = obj.pk
            if obj.parent_id:
                try:
                    parent = Page.objects.get(pk=obj.parent_id)
                except Page.DoesNotExist:
                    parent = None
            else:
                parent = None
            obj.pk = None
            obj.path = None
            obj.numchild = 0
            obj.depth = 0
            if parent:
                saved_obj = parent.add_child(instance=obj)
            else:
                saved_obj = obj.add_root(instance=obj)
            tmp_pk = saved_obj.pk
            saved_obj.pk = pk
            Page.objects.get(pk=tmp_pk).delete()
            saved_obj.save(no_signals=True)
        else:
            if 'history' in request.path_info:
                old_obj = Page.objects.get(pk=obj.pk)
                obj.depth = old_obj.depth
                obj.parent_id = old_obj.parent_id
                obj.path = old_obj.path
                obj.numchild = old_obj.numchild
        new = False
        if not obj.pk:
            new = True
        obj.save()

        if 'recover' in request.path_info or 'history' in request.path_info:
            revert_plugins(request, obj.version.pk, obj)

        if target is not None and position is not None:
            try:
                target = self.model.objects.get(pk=target)
            except self.model.DoesNotExist:
                pass
            else:
                if position == 'last-child' or position == 'first-child':
                    obj.parent_id = target.pk
                else:
                    obj.parent_id = target.parent_id
                obj.save()
                obj = obj.move(target, pos=position)
        page_type_id = form.cleaned_data.get('page_type')
        copy_target_id = request.GET.get('copy_target')
        if copy_target_id or page_type_id:
            if page_type_id:
                copy_target_id = page_type_id
            copy_target = Page.objects.get(pk=copy_target_id)
            if not copy_target.has_view_permission(request):
                raise PermissionDenied()
            obj = obj.reload()
            copy_target._copy_attributes(obj, clean=True)
            obj.save()
            for lang in copy_target.languages.split(','):
                copy_target._copy_contents(obj, lang)
        if not 'permission' in request.path_info:
            language = form.cleaned_data['language']
            Title.objects.set_or_create(
                request,
                obj,
                form,
                language,
            )
        # is it home? publish it right away
        if new and Page.objects.filter(site_id=obj.site_id).count() == 1:
            obj.publish(language)