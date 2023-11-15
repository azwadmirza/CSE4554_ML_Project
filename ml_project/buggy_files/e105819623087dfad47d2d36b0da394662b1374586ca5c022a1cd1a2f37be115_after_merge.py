def main():
    logger.info("Starting bootloader server")
    mongo_url = os.environ.get('MONGO_URL', env.get_mongo_url())
    bootloader_server_thread = Thread(target=BootloaderHttpServer(mongo_url).serve_forever, daemon=True)

    bootloader_server_thread.start()
    start_island_server()
    bootloader_server_thread.join()