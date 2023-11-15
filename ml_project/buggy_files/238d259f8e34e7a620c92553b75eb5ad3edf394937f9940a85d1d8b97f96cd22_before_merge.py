    def state_delete_category(self):
        """Delete category."""
        category_id = self.global_categories[self.category_name]['category_id']
        self.category_service.delete(category_id=category_id)
        self.module.exit_json(changed=True,
                              category_results=dict(msg="Category '%s' deleted." % self.category_name,
                                                    category_id=category_id))