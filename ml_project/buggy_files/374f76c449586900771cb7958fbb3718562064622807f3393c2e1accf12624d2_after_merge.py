    def __init__(self, model):
        self.model = model
        self.domain = model.domain
        self.instances = model.instances
        self.instances_transformed = self.instances.transform(self.domain)