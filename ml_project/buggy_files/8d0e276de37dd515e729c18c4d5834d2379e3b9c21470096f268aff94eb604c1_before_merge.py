def _handle_download_error(err, peer, blob_to_download):
    if not err.check(DownloadCanceledError, PriceDisagreementError, RequestCanceledError):
        log.warning("An error occurred while downloading %s from %s. Error: %s",
                    blob_to_download.blob_hash, str(peer), err.getTraceback())
    if err.check(PriceDisagreementError):
        # Don't kill the whole connection just because a price couldn't be agreed upon.
        # Other information might be desired by other request creators at a better rate.
        return True
    return err