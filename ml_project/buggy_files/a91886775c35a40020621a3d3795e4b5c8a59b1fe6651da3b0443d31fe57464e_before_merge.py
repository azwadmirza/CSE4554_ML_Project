        def run_on_thread(thread_method):
            # We are running code that writes to the wallet on a separate thread.
            # This is done because ethereum does not allow writing to a wallet from a daemon thread.
            wallet_thread = Thread(target=thread_method, name="ethereum-create-wallet")
            wallet_thread.setDaemon(False)
            wallet_thread.start()
            wallet_thread.join()