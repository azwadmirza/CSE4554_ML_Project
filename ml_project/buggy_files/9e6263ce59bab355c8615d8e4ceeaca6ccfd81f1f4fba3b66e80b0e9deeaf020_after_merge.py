    def state_update_category(self):
        """Update category."""
        category_id = self.global_categories[self.category_name]['category_id']
        changed = False
        results = dict(msg="Category %s is unchanged." % self.category_name,
                       category_id=category_id)

        category_update_spec = self.category_service.UpdateSpec()
        change_list = []
        old_cat_desc = self.global_categories[self.category_name]['category_description']
        new_cat_desc = self.params.get('category_description')
        if new_cat_desc and new_cat_desc != old_cat_desc:
            category_update_spec.description = new_cat_desc
            results['msg'] = 'Category %s updated.' % self.category_name
            change_list.append(True)

        new_cat_name = self.params.get('new_category_name')
        if new_cat_name in self.global_categories:
            self.module.fail_json(msg="Unable to rename %s as %s already"
                                      " exists in configuration." % (self.category_name, new_cat_name))
        old_cat_name = self.global_categories[self.category_name]['category_name']

        if new_cat_name and new_cat_name != old_cat_name:
            category_update_spec.name = new_cat_name
            results['msg'] = 'Category %s updated.' % self.category_name
            change_list.append(True)

        if any(change_list):
            try:
                self.category_service.update(category_id, category_update_spec)
                changed = True
            except Error as error:
                self.module.fail_json(msg="%s" % self.get_error_message(error))

        self.module.exit_json(changed=changed,
                              category_results=results)