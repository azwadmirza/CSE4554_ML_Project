    def loss(self, y_pred, target, scaling):
        return (y_pred - target).abs() / scaling.unsqueeze(-1)