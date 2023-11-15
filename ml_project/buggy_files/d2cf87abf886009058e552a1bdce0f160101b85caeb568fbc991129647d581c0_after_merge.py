        def get_base_samples(self, sample_shape=torch.Size()):
            """Get i.i.d. standard Normal samples (to be used with rsample(base_samples=base_samples))"""
            return super().get_base_samples(sample_shape=sample_shape)