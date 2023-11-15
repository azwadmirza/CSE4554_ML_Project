    def __init__(self, graph, data_transformer, y_encoder, metric, inverse_transform_y_method):
        """Initialize the instance.
        Args:
            graph: The graph form of the learned model
        """
        super().__init__(graph)
        self.data_transformer = data_transformer
        self.y_encoder = y_encoder
        self.metric = metric
        self.inverse_transform_y_method = inverse_transform_y_method