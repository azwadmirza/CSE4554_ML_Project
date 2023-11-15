    async def check_new_version_api(self, version_check_url):
        try:
            async with ClientSession(raise_for_status=True) as session:
                response = await session.get(version_check_url, timeout=ClientTimeout(total=VERSION_CHECK_TIMEOUT))
                response_dict = await response.json(content_type=None)
                version = response_dict['name'][1:]
                if LooseVersion(version) > LooseVersion(version_id):
                    self.session.notifier.notify(NTFY.TRIBLER_NEW_VERSION, version)
                    return True
                return False
        except (ServerConnectionError, ClientConnectionError) as e:
            self._logger.error("Error when performing version check request: %s", e)
            return False
        except ClientResponseError as e:
            self._logger.warning("Got response code %s when performing version check request", e.status)
            return False
        except ContentTypeError:
            self._logger.warning("Response was not in JSON format")
            return False
        except asyncio.TimeoutError:
            self._logger.warning("Checking for new version failed for %s", version_check_url)
            return False
        except ValueError as ve:
            raise ValueError("Failed to parse Tribler version response.\nError:%s" % ve)