    def load_checkpoint(*, filename, state: _State):
        if os.path.isfile(filename):
            print(f"=> loading checkpoint {filename}")
            checkpoint = utils.load_checkpoint(filename)

            state.epoch = checkpoint["epoch"]

            utils.unpack_checkpoint(
                checkpoint,
                model=state.model,
                criterion=state.criterion,
                optimizer=state.optimizer,
                scheduler=state.scheduler
            )

            print(
                f"loaded checkpoint {filename} (epoch {checkpoint['epoch']})"
            )
        else:
            raise Exception(f"No checkpoint found at {filename}")