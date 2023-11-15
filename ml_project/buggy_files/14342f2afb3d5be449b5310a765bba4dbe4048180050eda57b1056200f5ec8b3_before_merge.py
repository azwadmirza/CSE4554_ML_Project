    def __init__(self, model, hidden_dim=None, prefix="auto"):
        self.hidden_dim = hidden_dim
        self.arn = None
        super(AutoIAFNormal, self).__init__(model, prefix)