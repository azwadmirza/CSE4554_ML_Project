    def _load_effective_address(self, indices):
        return cgutils.get_item_pointer2(self.context,
                                         self.builder,
                                         data=self.data,
                                         shape=self.shape,
                                         strides=self.strides,
                                         layout=self.layout,
                                         inds=indices)