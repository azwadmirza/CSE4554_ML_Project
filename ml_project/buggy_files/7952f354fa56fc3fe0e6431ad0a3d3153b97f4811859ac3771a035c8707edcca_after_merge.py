    async def refresh(self, device=None, skip_api: bool = False):
        """Refresh device data.

        This is a per device refresh and for many Alexa devices can result in
        many refreshes from each individual device. This will call the
        AlexaAPI directly.

        Args:
        device (json): A refreshed device json from Amazon. For efficiency,
                       an individual device does not refresh if it's reported
                       as offline.
        skip_api (bool): Whether to only due a device json update and not hit the API

        """
        self.check_login_changes()
        if device is not None:
            self._device_name = device["accountName"]
            self._device_family = device["deviceFamily"]
            self._device_type = device["deviceType"]
            self._device_serial_number = device["serialNumber"]
            self._app_device_list = device["appDeviceList"]
            self._device_owner_customer_id = device["deviceOwnerCustomerId"]
            self._software_version = device["softwareVersion"]
            self._available = device["online"]
            self._capabilities = device["capabilities"]
            self._cluster_members = device["clusterMembers"]
            self._parent_clusters = device["parentClusters"]
            self._bluetooth_state = device["bluetooth_state"]
            self._locale = device["locale"] if "locale" in device else "en-US"
            self._timezone = device["timeZoneId"] if "timeZoneId" in device else "UTC"
            self._dnd = device["dnd"] if "dnd" in device else None
            self._set_authentication_details(device["auth_info"])
        session = None
        if self.available:
            _LOGGER.debug("%s: Refreshing %s", self.account, self.name)
            if "PAIR_BT_SOURCE" in self._capabilities:
                self._source = self._get_source()
                self._source_list = self._get_source_list()
                self._connected_bluetooth = self._get_connected_bluetooth()
                self._bluetooth_list = self._get_bluetooth_list()
            self._last_called = self._get_last_called()
            if self._last_called:
                self._last_called_timestamp = self.hass.data[DATA_ALEXAMEDIA][
                    "accounts"
                ][self._login.email]["last_called"]["timestamp"]
            if skip_api:
                return
            if "MUSIC_SKILL" in self._capabilities:
                if self._parent_clusters and self.hass:
                    playing_parents = list(
                        filter(
                            lambda x: (
                                self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                    self._login.email
                                ]["entities"]["media_player"].get(x)
                                and self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                    self._login.email
                                ]["entities"]["media_player"][x].state
                                == STATE_PLAYING
                            ),
                            self._parent_clusters,
                        )
                    )
                else:
                    playing_parents = []
                parent_session = {}
                if playing_parents:
                    if len(playing_parents) > 1:
                        _LOGGER.warning(
                            "Found multiple playing parents " "please file an issue"
                        )
                    parent = self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                        self._login.email
                    ]["entities"]["media_player"][playing_parents[0]]
                    self._playing_parent = parent
                    parent_session = parent.session
                if parent_session:
                    session = parent_session.copy()
                    session["isPlayingInLemur"] = False
                    session["lemurVolume"] = None
                    session["volume"] = (
                        parent_session["lemurVolume"]["memberVolume"][
                            self.device_serial_number
                        ]
                        if parent_session.get("lemurVolume")
                        and parent_session.get("lemurVolume", {})
                        .get("memberVolume", {})
                        .get(self.device_serial_number)
                        else session["volume"]
                    )
                    session = {"playerInfo": session}
                else:
                    self._playing_parent = None
                    session = await self.alexa_api.get_state()
        self._clear_media_details()
        # update the session if it exists
        self._session = session if session else None
        if self._session and self._session.get("playerInfo"):
            self._session = self._session["playerInfo"]
            if self._session.get("transport"):
                self._shuffle = (
                    self._session["transport"]["shuffle"] == "SELECTED"
                    if (
                        "shuffle" in self._session["transport"]
                        and self._session["transport"]["shuffle"] != "DISABLED"
                    )
                    else None
                )
                self._repeat = (
                    self._session["transport"]["repeat"] == "SELECTED"
                    if (
                        "repeat" in self._session["transport"]
                        and self._session["transport"]["repeat"] != "DISABLED"
                    )
                    else None
                )
            if self._session.get("state"):
                self._media_player_state = self._session["state"]
                self._media_pos = self._session.get("progress", {}).get("mediaProgress")
                self._media_title = self._session.get("infoText", {}).get("title")
                self._media_artist = self._session.get("infoText", {}).get("subText1")
                self._media_album_name = self._session.get("infoText", {}).get(
                    "subText2"
                )
                self._media_image_url = (
                    self._session.get("mainArt", {}).get("url")
                    if self._session.get("mainArt")
                    else None
                )
                self._media_duration = self._session.get("progress", {}).get(
                    "mediaLength"
                )
                if not self._session.get("lemurVolume"):
                    self._media_is_muted = (
                        self._session.get("volume", {}).get("muted")
                        if self._session.get("volume")
                        else self._media_is_muted
                    )
                    self._media_vol_level = (
                        self._session["volume"]["volume"] / 100
                        if self._session.get("volume")
                        and self._session.get("volume", {}).get("volume")
                        else self._media_vol_level
                    )
                else:
                    self._media_is_muted = (
                        self._session.get("lemurVolume", {})
                        .get("compositeVolume", {})
                        .get("muted")
                    )
                    self._media_vol_level = (
                        self._session["lemurVolume"]["compositeVolume"]["volume"] / 100
                        if (
                            self._session.get("lemurVolume", {})
                            .get("compositeVolume", {})
                            .get("volume")
                        )
                        else self._media_vol_level
                    )
                if self.hass and self._session.get("isPlayingInLemur"):
                    asyncio.gather(
                        *map(
                            lambda x: (
                                self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                    self._login.email
                                ]["entities"]["media_player"][x].async_update()
                            ),
                            filter(
                                lambda x: (
                                    self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                        self._login.email
                                    ]["entities"]["media_player"].get(x)
                                    and self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                        self._login.email
                                    ]["entities"]["media_player"][x].available
                                ),
                                self._cluster_members,
                            ),
                        )
                    )