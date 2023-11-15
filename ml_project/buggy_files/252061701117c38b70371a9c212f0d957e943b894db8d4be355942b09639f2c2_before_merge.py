    def state_create_category(self):
        """Create category."""
        category_spec = self.category_service.CreateSpec()
        category_spec.name = self.category_name
        category_spec.description = self.params.get('category_description')

        if self.params.get('category_cardinality') == 'single':
            category_spec.cardinality = CategoryModel.Cardinality.SINGLE
        else:
            category_spec.cardinality = CategoryModel.Cardinality.MULTIPLE

        category_spec.associable_types = set()

        category_id = self.category_service.create(category_spec)
        if category_id:
            self.module.exit_json(changed=True,
                                  category_results=dict(msg="Category '%s' created." % category_spec.name,
                                                        category_id=category_id))
        self.module.exit_json(changed=False,
                              category_results=dict(msg="No category created", category_id=''))