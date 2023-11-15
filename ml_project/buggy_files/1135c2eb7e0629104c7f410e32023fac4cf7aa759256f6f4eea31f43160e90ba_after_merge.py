    def can_change(self, obj, data):
        # Checks for admin change permission on inventory.
        if obj and obj.inventory:
            return (
                self.user.can_access(Inventory, 'change', obj.inventory, None) and
                self.check_related('source_project', Project, data, obj=obj, role_field='use_role')
            )
        # Can't change inventory sources attached to only the inventory, since
        # these are created automatically from the management command.
        else:
            return False