    def _apply_transforms(self, element, data, ranges, style, group=None):
        if element.ndims > 0:
            element = element.aggregate(function=np.mean)
        else:
            element = element.clone([(element.aggregate(function=np.mean),)])
        return super(BoxWhiskerPlot, self)._apply_transforms(element, data, ranges, style, group)