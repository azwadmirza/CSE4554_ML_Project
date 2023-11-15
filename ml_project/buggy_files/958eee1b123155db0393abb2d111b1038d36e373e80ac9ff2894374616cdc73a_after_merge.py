    async def refresh(self, device=None):
        """Refresh device data.

        This is a per device refresh and for many Alexa devices can result in
        many refreshes from each individual device. This will call the
        AlexaAPI directly.

        Args:
        device (json): A refreshed device json from Amazon. For efficiency,
                       an individual device does not refresh if it's reported
                       as offline.

        """
        if device is not None:
            self._device = device
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
            await self._set_authentication_details(device["auth_info"])
        session = None
        if self._available:
            _LOGGER.debug("%s: Refreshing %s", self.account, self.name)
            if self._parent_clusters and self.hass:
                playing_parents = list(
                    filter(
                        lambda x: (
                            self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                self._login.email
                            ]["entities"]["media_player"].get(x)
                            and
                            self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                self._login.email
                            ]["entities"]["media_player"][x].state
                            == STATE_PLAYING
                        ),
                        self._parent_clusters,
                    )
                )
            else:
                playing_parents = []
            if "PAIR_BT_SOURCE" in self._capabilities:
                self._source = await self._get_source()
                self._source_list = await self._get_source_list()
            self._last_called = await self._get_last_called()
            if "MUSIC_SKILL" in self._capabilities:
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
                        if parent_session["lemurVolume"]
                        and "memberVolume" in parent_session["lemurVolume"]
                        else session["volume"]
                    )
                    session = {"playerInfo": session}
                else:
                    self._playing_parent = None
                    session = await self.alexa_api.get_state()
        await self._clear_media_details()
        # update the session if it exists; not doing relogin here
        if session:
            self._session = session
        if self._session and "playerInfo" in self._session:
            self._session = self._session["playerInfo"]
            if self._session["transport"] is not None:
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
            if self._session["state"] is not None:
                self._media_player_state = self._session["state"]
                self._media_pos = (
                    self._session["progress"]["mediaProgress"]
                    if (
                        self._session["progress"] is not None
                        and "mediaProgress" in self._session["progress"]
                    )
                    else None
                )
                self._media_title = (
                    self._session["infoText"]["title"]
                    if (
                        self._session["infoText"] is not None
                        and "title" in self._session["infoText"]
                    )
                    else None
                )
                self._media_artist = (
                    self._session["infoText"]["subText1"]
                    if (
                        self._session["infoText"] is not None
                        and "subText1" in self._session["infoText"]
                    )
                    else None
                )
                self._media_album_name = (
                    self._session["infoText"]["subText2"]
                    if (
                        self._session["infoText"] is not None
                        and "subText2" in self._session["infoText"]
                    )
                    else None
                )
                self._media_image_url = (
                    self._session["mainArt"]["url"]
                    if (
                        self._session["mainArt"] is not None
                        and "url" in self._session["mainArt"]
                    )
                    else None
                )
                self._media_duration = (
                    self._session["progress"]["mediaLength"]
                    if (
                        self._session["progress"] is not None
                        and "mediaLength" in self._session["progress"]
                    )
                    else None
                )
                if not self._session["lemurVolume"]:
                    self._media_is_muted = (
                        self._session["volume"]["muted"]
                        if (
                            self._session["volume"] is not None
                            and "muted" in self._session["volume"]
                        )
                        else None
                    )
                    self._media_vol_level = (
                        self._session["volume"]["volume"] / 100
                        if (
                            self._session["volume"] is not None
                            and "volume" in self._session["volume"]
                        )
                        else self._media_vol_level
                    )
                else:
                    self._media_is_muted = (
                        self._session["lemurVolume"]["compositeVolume"]["muted"]
                        if (
                            self._session["lemurVolume"]
                            and "compositeVolume" in self._session["lemurVolume"]
                            and self._session["lemurVolume"]["compositeVolume"]
                            and "muted"
                            in self._session["lemurVolume"]["compositeVolume"]
                        )
                        else None
                    )
                    self._media_vol_level = (
                        self._session["lemurVolume"]["compositeVolume"]["volume"] / 100
                        if (
                            self._session["lemurVolume"]
                            and "compositeVolume" in self._session["lemurVolume"]
                            and "volume"
                            in self._session["lemurVolume"]["compositeVolume"]
                            and (
                                self._session["lemurVolume"]["compositeVolume"][
                                    "volume"
                                ]
                            )
                        )
                        else self._media_vol_level
                    )
                    if not self.hass:
                        return
                    asyncio.gather(
                        *map(
                            lambda x: (
                                self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                    self._login.email
                                ]["entities"]["media_player"][x].async_update()
                            ),
                            filter(
                                lambda x: (
                                    x
                                    in (
                                        self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                            self._login.email
                                        ]["entities"]["media_player"]
                                    )
                                    and self.hass.data[DATA_ALEXAMEDIA]["accounts"][
                                        self._login.email
                                    ]["entities"]["media_player"][x].available
                                ),
                                self._cluster_members,
                            ),
                        )
                    )