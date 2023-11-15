    def guide(self, xs, ys=None):
        """
        The guide corresponds to the following:
        q(y|x) = categorical(alpha(x))              # infer digit from an image
        q(z|x,y) = normal(mu(x,y),sigma(x,y))       # infer handwriting style from an image and the digit
        mu, sigma are given by a neural network `encoder_z`
        alpha is given by a neural network `encoder_y`
        :param xs: a batch of scaled vectors of pixels from an image
        :param ys: (optional) a batch of the class labels i.e.
                   the digit corresponding to the image(s)
        :return: None
        """
        # inform Pyro that the variables in the batch of xs, ys are conditionally independent
        with pyro.iarange("independent"):

            # if the class label (the digit) is not supervised, sample
            # (and score) the digit with the variational distribution
            # q(y|x) = categorical(alpha(x))
            if ys is None:
                alpha = self.encoder_y.forward(xs)
                ys = pyro.sample("y", dist.one_hot_categorical, alpha)

            # sample (and score) the latent handwriting-style with the variational
            # distribution q(z|x,y) = normal(mu(x,y),sigma(x,y))
            mu, sigma = self.encoder_z.forward([xs, ys])
            pyro.sample("z", dist.normal, mu, sigma, extra_event_dims=1)