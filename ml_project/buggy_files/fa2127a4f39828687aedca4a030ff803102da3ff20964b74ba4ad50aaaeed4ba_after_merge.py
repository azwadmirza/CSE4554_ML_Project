    async def handle_request(self, request: BlobRequest):
        addr = self.transport.get_extra_info('peername')
        peer_address, peer_port = addr

        responses = []
        address_request = request.get_address_request()
        if address_request:
            responses.append(BlobPaymentAddressResponse(lbrycrd_address=self.lbrycrd_address))
        availability_request = request.get_availability_request()
        if availability_request:
            responses.append(BlobAvailabilityResponse(available_blobs=list(set(
                filter(lambda blob_hash: blob_hash in self.blob_manager.completed_blob_hashes,
                       availability_request.requested_blobs)
            ))))
        price_request = request.get_price_request()
        if price_request:
            responses.append(BlobPriceResponse(blob_data_payment_rate='RATE_ACCEPTED'))
        download_request = request.get_blob_request()

        if download_request:
            blob = self.blob_manager.get_blob(download_request.requested_blob)
            if blob.get_is_verified():
                incoming_blob = {'blob_hash': blob.blob_hash, 'length': blob.length}
                responses.append(BlobDownloadResponse(incoming_blob=incoming_blob))
                self.send_response(responses)
                blob_hash = blob.blob_hash[:8]
                log.debug("send %s to %s:%i", blob_hash, peer_address, peer_port)
                self.started_transfer.set()
                try:
                    sent = await asyncio.wait_for(blob.sendfile(self), self.transfer_timeout, loop=self.loop)
                    if sent and sent > 0:
                        self.blob_manager.connection_manager.sent_data(self.peer_address_and_port, sent)
                        log.info("sent %s (%i bytes) to %s:%i", blob_hash, sent, peer_address, peer_port)
                    else:
                        self.close()
                        log.debug("stopped sending %s to %s:%i", blob_hash, peer_address, peer_port)
                        return
                except (OSError, ValueError, asyncio.TimeoutError) as err:
                    if isinstance(err, asyncio.TimeoutError):
                        log.debug("timed out sending blob %s to %s", blob_hash, peer_address)
                    else:
                        log.warning("could not read blob %s to send %s:%i", blob_hash, peer_address, peer_port)
                    self.close()
                    return
                finally:
                    self.transfer_finished.set()
            else:
                log.info("don't have %s to send %s:%i", blob.blob_hash[:8], peer_address, peer_port)
        if responses and not self.transport.is_closing():
            self.send_response(responses)