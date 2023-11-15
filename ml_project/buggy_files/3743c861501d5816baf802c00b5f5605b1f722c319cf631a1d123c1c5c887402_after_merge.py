    def data(self, index, role):
        # Return tooltip for state indicator column
        if role == Qt.ToolTipRole:
            if index.column() == self.column_position[u'state']:
                return self.data_items[index.row()].get(u'state')
            return None
        else:
            return super(StateTooltipMixin, self).data(index, role)