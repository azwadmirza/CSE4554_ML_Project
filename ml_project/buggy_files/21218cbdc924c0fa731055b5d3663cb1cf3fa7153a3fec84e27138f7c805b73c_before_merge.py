    def model(self, xs, ys=None):
        """
        The model corresponds to the following generative process:
        p(z) = normal(0,I)              # handwriting style (latent)
        p(y|x) = categorical(I/10.)     # which digit (semi-supervised)
        p(x|y,z) = bernoulli(mu(y,z))   # an image
        mu is given by a neural network  `decoder`

        :param xs: a batch of scaled vectors of pixels from an image
        :param ys: (optional) a batch of the class labels i.e.
                   the digit corresponding to the image(s)
        :return: None
        """
        # register this pytorch module and all of its sub-modules with pyro
        pyro.module("ss_vae", self)

        batch_size = xs.size(0)
        with pyro.iarange("independent"):

            # sample the handwriting style from the constant prior distribution
            prior_mu = Variable(torch.zeros([batch_size, self.z_dim]))
            prior_sigma = Variable(torch.ones([batch_size, self.z_dim]))
            zs = pyro.sample("z", dist.normal, prior_mu, prior_sigma)

            # if the label y (which digit to write) is supervised, sample from the
            # constant prior, otherwise, observe the value (i.e. score it against the constant prior)
            alpha_prior = Variable(torch.ones([batch_size, self.output_size]) / (1.0 * self.output_size))
            if ys is None:
                ys = pyro.sample("y", dist.one_hot_categorical, alpha_prior)
            else:
                pyro.sample("y", dist.one_hot_categorical, alpha_prior, obs=ys)

            # finally, score the image (x) using the handwriting style (z) and
            # the class label y (which digit to write) against the
            # parametrized distribution p(x|y,z) = bernoulli(decoder(y,z))
            # where `decoder` is a neural network
            mu = self.decoder.forward([zs, ys])
            pyro.sample("x", dist.bernoulli, mu, obs=xs)