    def get_base_class_hook(self, fullname: str
                            ) -> Optional[Callable[[ClassDefContext], None]]:
        if (fullname in self.django_context.all_registered_model_class_fullnames
                or fullname in self._get_current_model_bases()):
            return partial(transform_model_class, django_context=self.django_context)

        if fullname in self._get_current_manager_bases():
            return add_new_manager_base

        if fullname in self._get_current_form_bases():
            return transform_form_class
        return None