    def attribute(self, node):
        feature_idx = self.splitting_attribute(node)
        if feature_idx == self.FEATURE_UNDEFINED:
            return None
        return self.domain.attributes[self.splitting_attribute(node)]