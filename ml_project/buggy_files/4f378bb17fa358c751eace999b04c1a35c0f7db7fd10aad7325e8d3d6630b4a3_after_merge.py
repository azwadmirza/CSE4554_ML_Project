def screencast_service():
    """Start or Stop ScreenCast Services"""
    global TCP_SERVER_MODE
    logger.info("ScreenCast Service Status: " + TCP_SERVER_MODE)
    try:
        screen_dir = settings.SCREEN_DIR
        if not os.path.exists(screen_dir):
            os.makedirs(screen_dir)

        screen_socket = socket.socket()
        if TCP_SERVER_MODE == "on":
            screen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                addr = ('127.0.0.1', settings.SCREEN_PORT)
            else:
                addr = (settings.SCREEN_IP, settings.SCREEN_PORT)
            screen_socket.bind(addr)
            screen_socket.listen(10)
            while TCP_SERVER_MODE == "on":
                screens, address = screen_socket.accept()
                logger.info("Got Connection from: %s", address[0])
                if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_REAL_DEVICE":
                    ip_address = settings.DEVICE_IP
                else:
                    ip_address = settings.VM_IP
                if address[0] in [ip_address, '127.0.0.1']:
                    # Very Basic Check to ensure that only MobSF VM/Device/Emulator
                    # is allowed to connect to MobSF ScreenCast Service.
                    with open(screen_dir + 'screen.png', 'wb') as flip:
                        while True:
                            data = screens.recv(1024)
                            if not data:
                                break
                            flip.write(data)
                else:
                    logger.warning("\n[ATTACK] An unknown client :" + address[0] + " is trying " +
                                "to make a connection with MobSF ScreenCast Service!")
        elif TCP_SERVER_MODE == "off":
            screen_socket.close()
    except:
        screen_socket.close()
        PrintException("ScreenCast Server")