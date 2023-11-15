    def _apply_transforms(self, element, data, ranges, style, group=None):
        if element.ndims > 0:
            element = element.aggregate(function=np.mean)
        else:
            agg = element.aggregate(function=np.mean)
            if isinstance(agg, Dimensioned):
                element = agg
            else:
                element = element.clone([(element,)])
        return super(BoxWhiskerPlot, self)._apply_transforms(element, data, ranges, style, group)