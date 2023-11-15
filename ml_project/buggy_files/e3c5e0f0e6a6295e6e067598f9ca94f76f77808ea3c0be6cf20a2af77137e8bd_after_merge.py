    def __init__(self, a, b, sigma=0.01, validate_args=False, transform=None):
        TModule.__init__(self)
        _a = torch.tensor(float(a)) if isinstance(a, Number) else a
        _a = _a.view(-1) if _a.dim() < 1 else _a
        _a, _b, _sigma = broadcast_all(_a, b, sigma)
        if not torch.all(constraints.less_than(_b).check(_a)):
            raise ValueError("must have that a < b (element-wise)")
        # TODO: Proper argument validation including broadcasting
        batch_shape, event_shape = _a.shape[:-1], _a.shape[-1:]
        # need to assign values before registering as buffers to make argument validation work
        self.a, self.b, self.sigma = _a, _b, _sigma
        super(SmoothedBoxPrior, self).__init__(batch_shape, event_shape, validate_args=validate_args)
        # now need to delete to be able to register buffer
        del self.a, self.b, self.sigma
        self.register_buffer("a", _a)
        self.register_buffer("b", _b)
        self.register_buffer("sigma", _sigma.clone())
        self.tails = NormalPrior(torch.zeros_like(_a), _sigma, validate_args=validate_args)
        self._transform = transform