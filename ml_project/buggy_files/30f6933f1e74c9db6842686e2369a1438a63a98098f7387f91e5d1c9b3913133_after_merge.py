    def __init__(self, device, handle, finalizer=None):
        self.device = device
        self.handle = handle
        self.external_finalizer = finalizer
        self.trashing = TrashService("cuda.device%d.context%x.trash" %
                                     (self.device.id, self.handle.value))
        self.allocations = utils.UniqueDict()
        self.modules = utils.UniqueDict()
        self.finalizer = utils.finalize(self, self._make_finalizer())
        # For storing context specific data
        self.extras = {}