    def state_delete_category(self):
        """Delete category."""
        category_id = self.global_categories[self.category_name]['category_id']
        try:
            self.category_service.delete(category_id=category_id)
        except Error as error:
            self.module.fail_json(msg="%s" % self.get_error_message(error))
        self.module.exit_json(changed=True,
                              category_results=dict(msg="Category '%s' deleted." % self.category_name,
                                                    category_id=category_id))