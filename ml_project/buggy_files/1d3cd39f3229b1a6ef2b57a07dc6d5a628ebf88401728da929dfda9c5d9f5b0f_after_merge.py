    def deploy(
        self,
        contract: Any,
        *args: Tuple,
        amount: int = 0,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        nonce: Optional[int] = None,
    ) -> Any:
        """Deploys a contract.

        Args:
            contract: ContractContainer instance.
            *args: Constructor arguments. The last argument may optionally be
                   a dictionary of transaction values.

        Kwargs:
            amount: Amount of ether to send with transaction, in wei.
            gas_limit: Gas limit of the transaction.
            gas_price: Gas price of the transaction.
            nonce: Nonce to use for the transaction.

        Returns:
            * Contract instance if the transaction confirms and the contract exists
            * TransactionReceipt if the transaction is pending or reverts
        """

        evm = contract._build["compiler"]["evm_version"]
        if rpc.is_active() and not rpc.evm_compatible(evm):
            raise IncompatibleEVMVersion(
                f"Local RPC using '{rpc.evm_version()}' but contract was compiled for '{evm}'"
            )
        data = contract.deploy.encode_input(*args)
        try:
            txid = self._transact(  # type: ignore
                {
                    "from": self.address,
                    "value": Wei(amount),
                    "nonce": nonce if nonce is not None else self.nonce,
                    "gasPrice": Wei(gas_price) or self._gas_price(),
                    "gas": Wei(gas_limit) or self._gas_limit(None, amount, data),
                    "data": HexBytes(data),
                }
            )
            exc, revert_data = None, None
        except ValueError as e:
            exc = VirtualMachineError(e)
            if not hasattr(exc, "txid"):
                raise exc from None
            txid = exc.txid
            revert_data = (exc.revert_msg, exc.pc, exc.revert_type)

        receipt = TransactionReceipt(
            txid, self, name=contract._name + ".constructor", revert_data=revert_data
        )
        add_thread = threading.Thread(target=contract._add_from_tx, args=(receipt,), daemon=True)
        add_thread.start()

        if rpc.is_active():
            undo_thread = threading.Thread(
                target=rpc._add_to_undo_buffer,
                args=(
                    receipt,
                    self.deploy,
                    (contract, *args),
                    {"amount": amount, "gas_limit": gas_limit, "gas_price": gas_price},
                ),
                daemon=True,
            )
            undo_thread.start()

        if receipt.status != 1:
            receipt._raise_if_reverted(exc)
            return receipt

        add_thread.join()
        try:
            return contract.at(receipt.contract_address)
        except ContractNotFound:
            # if the contract self-destructed during deployment
            return receipt