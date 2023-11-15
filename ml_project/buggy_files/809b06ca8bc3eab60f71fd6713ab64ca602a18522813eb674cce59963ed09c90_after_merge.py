    def initialize_market_page(self):

        if not self.initialized:
            self.window().market_back_button.setIcon(QIcon(get_image_path('page_back.png')))

            self.window().core_manager.events_manager.received_market_ask.connect(self.on_ask)
            self.window().core_manager.events_manager.received_market_bid.connect(self.on_bid)
            self.window().core_manager.events_manager.expired_market_ask.connect(self.on_ask_timeout)
            self.window().core_manager.events_manager.expired_market_bid.connect(self.on_bid_timeout)
            self.window().core_manager.events_manager.market_payment_received.connect(self.on_payment)
            self.window().core_manager.events_manager.market_payment_sent.connect(self.on_payment)
            self.window().core_manager.events_manager.market_transaction_complete.connect(self.on_transaction_complete)

            self.window().create_ask_button.clicked.connect(self.on_create_ask_clicked)
            self.window().create_bid_button.clicked.connect(self.on_create_bid_clicked)
            self.window().market_currency_type_button.clicked.connect(self.on_asset_type_clicked)
            self.window().market_transactions_button.clicked.connect(self.on_transactions_button_clicked)
            self.window().market_wallets_button.clicked.connect(self.on_wallets_button_clicked)
            self.window().market_orders_button.clicked.connect(self.on_orders_button_clicked)
            self.window().market_create_wallet_button.clicked.connect(self.on_wallets_button_clicked)

            # Sort asks ascending and bids descending
            self.window().asks_list.sortItems(0, Qt.AscendingOrder)
            self.window().bids_list.sortItems(2, Qt.DescendingOrder)

            self.window().asks_list.itemSelectionChanged.connect(
                lambda: self.on_tick_item_clicked(self.window().asks_list))
            self.window().bids_list.itemSelectionChanged.connect(
                lambda: self.on_tick_item_clicked(self.window().bids_list))

            self.window().tick_detail_container.hide()
            self.window().market_create_wallet_button.hide()
            self.window().create_ask_button.hide()
            self.window().create_bid_button.hide()

            self.initialized = True

        self.load_wallets()