    def get_extra_context(self, request, instance):
        related_paths = []

        # If tracing a PathEndpoint, locate the CablePath (if one exists) by its origin
        if isinstance(instance, PathEndpoint):
            path = instance._path

        # Otherwise, find all CablePaths which traverse the specified object
        else:
            related_paths = CablePath.objects.filter(path__contains=instance).prefetch_related('origin')
            # Check for specification of a particular path (when tracing pass-through ports)
            try:
                path_id = int(request.GET.get('cablepath_id'))
            except TypeError:
                path_id = None
            if path_id in list(related_paths.values_list('pk', flat=True)):
                path = CablePath.objects.get(pk=path_id)
            else:
                path = related_paths.first()

        return {
            'path': path,
            'related_paths': related_paths,
            'total_length': path.get_total_length() if path else None,
        }