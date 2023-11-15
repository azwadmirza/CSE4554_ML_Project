    def run(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs
        num_samples = [0] * self.num_chains
        z_flat_acc = [[] for _ in range(self.num_chains)]
        with pyro.validation_enabled(not self.disable_validation):
            for x, chain_id in self.sampler.run(*args, **kwargs):
                if num_samples[chain_id] == 0:
                    num_samples[chain_id] += 1
                    z_structure = x
                elif num_samples[chain_id] == self.num_samples + 1:
                    self._diagnostics[chain_id] = x
                else:
                    num_samples[chain_id] += 1
                    if self.num_chains > 1:
                        x_cloned = x.clone()
                        del x
                    else:
                        x_cloned = x
                    z_flat_acc[chain_id].append(x_cloned)

        z_flat_acc = torch.stack([torch.stack(l) for l in z_flat_acc])

        # unpack latent
        pos = 0
        z_acc = z_structure.copy()
        for k in sorted(z_structure):
            shape = z_structure[k]
            next_pos = pos + shape.numel()
            z_acc[k] = z_flat_acc[:, :, pos:next_pos].reshape(
                (self.num_chains, self.num_samples) + shape)
            pos = next_pos
        assert pos == z_flat_acc.shape[-1]

        # If transforms is not explicitly provided, infer automatically using
        # model args, kwargs.
        if self.transforms is None:
            if hasattr(self.kernel, 'transforms'):
                if self.kernel.transforms is not None:
                    self.transforms = self.kernel.transforms
            elif self.kernel.model:
                _, _, self.transforms, _ = initialize_model(self.kernel.model,
                                                            model_args=args,
                                                            model_kwargs=kwargs)
            else:
                self.transforms = {}

        # transform samples back to constrained space
        for name, transform in self.transforms.items():
            z_acc[name] = transform.inv(z_acc[name])
        self._samples = z_acc

        # terminate the sampler (shut down worker processes)
        self.sampler.terminate(True)