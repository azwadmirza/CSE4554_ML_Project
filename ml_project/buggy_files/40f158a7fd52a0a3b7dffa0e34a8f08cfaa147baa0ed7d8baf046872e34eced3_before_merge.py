    def process_request(self, request):
        if migration_in_progress_check_or_relase():
            if getattr(resolve(request.path), 'url_name', '') == 'migrations_notran':
                return
            return redirect(reverse("ui:migrations_notran"))