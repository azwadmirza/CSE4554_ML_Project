    def model_sample(self, ys, batch_size=1):
        # sample the handwriting style from the constant prior distribution
        prior_mu = Variable(torch.zeros([batch_size, self.z_dim]))
        prior_sigma = Variable(torch.ones([batch_size, self.z_dim]))
        zs = pyro.sample("z", dist.normal, prior_mu, prior_sigma, extra_event_dims=1)

        # sample an image using the decoder
        mu = self.decoder.forward([zs, ys])
        xs = pyro.sample("sample", dist.bernoulli, mu, extra_event_dims=1)
        return xs, mu