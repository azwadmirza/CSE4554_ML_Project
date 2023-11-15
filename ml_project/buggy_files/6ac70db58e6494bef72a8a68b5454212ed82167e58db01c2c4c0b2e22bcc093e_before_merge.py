    def train_epoch(self, *pargs, **kwargs):
        # print(self.model)
        def benchmark():
            self.optimizer.zero_grad()
            output = self.model(self.data)
            loss = F.cross_entropy(output, self.target)
            loss.backward()
            self.optimizer.step()

        # print("Running warmup...")
        if self.global_step == 0:
            timeit.timeit(benchmark, number=args.num_warmup_batches)
            self.global_step += 1
        # print("Running benchmark...")
        time = timeit.timeit(benchmark, number=args.num_batches_per_iter)
        img_sec = args.batch_size * args.num_batches_per_iter / time
        return {"img_sec": img_sec}