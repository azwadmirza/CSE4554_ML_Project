    def get_additional_deps(self, file: MypyFile) -> List[Tuple[int, str, int]]:
        # for settings
        if file.fullname() == 'django.conf' and self.django_context.django_settings_module:
            return [self._new_dependency(self.django_context.django_settings_module)]

        # for values / values_list
        if file.fullname() == 'django.db.models':
            return [self._new_dependency('mypy_extensions'), self._new_dependency('typing')]

        # for `get_user_model()`
        if self.django_context.settings:
            if (file.fullname() == 'django.contrib.auth'
                    or file.fullname() in {'django.http', 'django.http.request'}):
                auth_user_model_name = self.django_context.settings.AUTH_USER_MODEL
                try:
                    auth_user_module = self.django_context.apps_registry.get_model(auth_user_model_name).__module__
                except LookupError:
                    # get_user_model() model app is not installed
                    return []
                return [self._new_dependency(auth_user_module)]

        # ensure that all mentioned to='someapp.SomeModel' are loaded with corresponding related Fields
        defined_model_classes = self.django_context.model_modules.get(file.fullname())
        if not defined_model_classes:
            return []
        deps = set()
        for model_class in defined_model_classes:
            # forward relations
            for field in self.django_context.get_model_fields(model_class):
                if isinstance(field, RelatedField):
                    related_model_cls = self.django_context.get_field_related_model_cls(field)
                    if related_model_cls is None:
                        continue
                    related_model_module = related_model_cls.__module__
                    if related_model_module != file.fullname():
                        deps.add(self._new_dependency(related_model_module))
            # reverse relations
            for relation in model_class._meta.related_objects:
                related_model_cls = self.django_context.get_field_related_model_cls(relation)
                related_model_module = related_model_cls.__module__
                if related_model_module != file.fullname():
                    deps.add(self._new_dependency(related_model_module))
        return list(deps)