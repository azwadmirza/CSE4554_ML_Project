    def pairing_dialog(self):
        def pairing_step(code: str, device_response: Callable[[], bool]) -> bool:
            msg = "Please compare and confirm the pairing code on your BitBox02:\n" + code
            self.handler.show_message(msg)
            try:
                res = device_response()
            except:
                # Close the hid device on exception
                hid_device.close()
                raise
            finally:
                self.handler.finished()
            return res

        def exists_remote_static_pubkey(pubkey: bytes) -> bool:
            bitbox02_config = self.config.get("bitbox02")
            noise_keys = bitbox02_config.get("remote_static_noise_keys")
            if noise_keys is not None:
                if pubkey.hex() in [noise_key for noise_key in noise_keys]:
                    return True
            return False

        def set_remote_static_pubkey(pubkey: bytes) -> None:
            if not exists_remote_static_pubkey(pubkey):
                bitbox02_config = self.config.get("bitbox02")
                if bitbox02_config.get("remote_static_noise_keys") is not None:
                    bitbox02_config["remote_static_noise_keys"].append(pubkey.hex())
                else:
                    bitbox02_config["remote_static_noise_keys"] = [pubkey.hex()]
                self.config.set_key("bitbox02", bitbox02_config)

        def get_noise_privkey() -> Optional[bytes]:
            bitbox02_config = self.config.get("bitbox02")
            privkey = bitbox02_config.get("noise_privkey")
            if privkey is not None:
                return bytes.fromhex(privkey)
            return None

        def set_noise_privkey(privkey: bytes) -> None:
            bitbox02_config = self.config.get("bitbox02")
            bitbox02_config["noise_privkey"] = privkey.hex()
            self.config.set_key("bitbox02", bitbox02_config)

        def attestation_warning() -> None:
            self.handler.show_error(
                "The BitBox02 attestation failed.\nTry reconnecting the BitBox02.\nWarning: The device might not be genuine, if the\n problem persists please contact Shift support.",
                blocking=True
            )

        class NoiseConfig(bitbox_api_protocol.BitBoxNoiseConfig):
            """NoiseConfig extends BitBoxNoiseConfig"""

            def show_pairing(self, code: str, device_response: Callable[[], bool]) -> bool:
                return pairing_step(code, device_response)

            def attestation_check(self, result: bool) -> None:
                if not result:
                    attestation_warning()

            def contains_device_static_pubkey(self, pubkey: bytes) -> bool:
                return exists_remote_static_pubkey(pubkey)

            def add_device_static_pubkey(self, pubkey: bytes) -> None:
                return set_remote_static_pubkey(pubkey)

            def get_app_static_privkey(self) -> Optional[bytes]:
                return get_noise_privkey()

            def set_app_static_privkey(self, privkey: bytes) -> None:
                return set_noise_privkey(privkey)

        if self.bitbox02_device is None:
            hid_device = hid.device()
            hid_device.open_path(self.bitbox_hid_info["path"])

            bitbox02_device = bitbox02.BitBox02(
                transport=u2fhid.U2FHid(hid_device),
                device_info=self.bitbox_hid_info,
                noise_config=NoiseConfig(),
            )
            try:
                bitbox02_device.check_min_version()
            except FirmwareVersionOutdatedException:
                raise
            self.bitbox02_device = bitbox02_device

        self.fail_if_not_initialized()