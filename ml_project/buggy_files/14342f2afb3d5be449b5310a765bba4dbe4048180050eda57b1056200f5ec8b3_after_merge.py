    def __init__(self, model, hidden_dim=None, prefix="auto", init_loc_fn=init_to_median):
        self.hidden_dim = hidden_dim
        self.arn = None
        super(AutoIAFNormal, self).__init__(model, prefix=prefix, init_loc_fn=init_loc_fn)