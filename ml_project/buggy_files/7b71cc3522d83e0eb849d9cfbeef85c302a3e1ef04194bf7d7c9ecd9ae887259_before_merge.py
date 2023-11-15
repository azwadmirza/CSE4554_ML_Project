    def get_data(self, element, ranges):
        neg_error = element.dimension_values(2)
        pos_idx = 3 if len(element.dimensions()) > 3 else 2
        pos_error = element.dimension_values(pos_idx)

        style = self.style[self.cyclic_index]
        error_y = dict(type='data', array=pos_error,
                       arrayminus=neg_error, visible=True, **style)
        return (), dict(x=element.dimension_values(0),
                        y=element.dimension_values(1),
                        error_y=error_y)