    def __init__(self, device, handle, finalizer=None):
        self.device = device
        self.handle = handle
        self.finalizer = finalizer
        self.trashing = TrashService("cuda.device%d.context%x.trash" %
                                     (self.device.id, self.handle.value))
        self.is_managed = finalizer is not None
        self.allocations = utils.UniqueDict()
        self.modules = utils.UniqueDict()
        # For storing context specific data
        self.extras = {}