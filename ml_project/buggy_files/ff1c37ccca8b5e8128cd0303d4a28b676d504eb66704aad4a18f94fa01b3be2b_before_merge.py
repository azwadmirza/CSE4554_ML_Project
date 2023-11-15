    def order_created(self, order: "Order", previous_value: Any) -> Any:
        if not self.active:
            return previous_value
        data = get_order_tax_data(order, self.config, force_refresh=True)

        transaction_url = urljoin(
            get_api_url(self.config.use_sandbox), "transactions/createoradjust"
        )
        api_post_request_task.delay(transaction_url, data, self.config)
        return previous_value