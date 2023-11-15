    def log(
        self,
        name: str,
        value: Any,
        prog_bar: bool = False,
        logger: bool = True,
        on_step: bool = False,
        on_epoch: bool = True,
        reduce_fx: Callable = torch.mean,
        tbptt_reduce_fx: Callable = torch.mean,
        tbptt_pad_token: int = 0,
        enable_graph: bool = False,
        sync_dist: bool = False,
        sync_dist_op: Union[Any, str] = 'mean',
        sync_dist_group: Optional[Any] = None,
        sync_fn: Callable = None,
        dataloader_idx: Optional[int] = None,
    ):
        # no metrics should be logged with graphs
        if not enable_graph and isinstance(value, torch.Tensor):
            value = value.detach()

        # sync across workers when using distributed training
        sync_fn = sync_fn or sync_ddp_if_available
        if sync_dist and isinstance(value, (torch.Tensor, numbers.Number)):
            value = sync_fn(value, group=sync_dist_group, reduce_op=sync_dist_op)

        if 'meta' not in self:
            self.__setitem__('meta', {})

        # if user requests both step and epoch, then we split the metric in two automatically
        # one will be logged per step. the other per epoch
        was_forked = False
        if on_step and on_epoch:
            was_forked = True

            # set step version
            step_name = f'{name}_step'

            self.__set_meta(
                step_name,
                value,
                prog_bar,
                logger,
                on_step=True,
                on_epoch=False,
                reduce_fx=reduce_fx,
                tbptt_reduce_fx=tbptt_reduce_fx,
                tbptt_pad_token=tbptt_pad_token,
                forked=False,
                dataloader_idx=dataloader_idx,
            )

            self.__setitem__(step_name, value)

            # set epoch version
            epoch_name = f'{name}_epoch'

            self.__set_meta(
                epoch_name,
                value,
                prog_bar,
                logger,
                on_step=False,
                on_epoch=True,
                reduce_fx=reduce_fx,
                tbptt_reduce_fx=tbptt_reduce_fx,
                tbptt_pad_token=tbptt_pad_token,
                forked=False,
                dataloader_idx=dataloader_idx,
            )
            self.__setitem__(epoch_name, value)

        # always log the original metric
        self.__set_meta(
            name,
            value,
            prog_bar,
            logger,
            on_step,
            on_epoch,
            reduce_fx,
            tbptt_reduce_fx=tbptt_reduce_fx,
            tbptt_pad_token=tbptt_pad_token,
            forked=was_forked,
            dataloader_idx=dataloader_idx,
        )

        # set the value
        self.__setitem__(name, value)