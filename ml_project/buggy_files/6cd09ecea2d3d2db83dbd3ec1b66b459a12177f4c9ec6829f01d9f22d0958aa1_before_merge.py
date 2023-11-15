    def websocket_emit_data(self):
        websocket_data = super(InventoryUpdate, self).websocket_emit_data()
        websocket_data.update(dict(inventory_source_id=self.inventory_source.pk))

        if self.inventory_source.inventory is not None:
            websocket_data.update(dict(inventory_id=self.inventory_source.inventory.pk))

        if self.inventory_source.deprecated_group is not None:  # TODO: remove in 3.3
            websocket_data.update(dict(group_id=self.inventory_source.deprecated_group.id))
        return websocket_data