    def _sendNMA(self, nma_api=None, nma_priority=None, event=None, message=None, force=False):

        title = 'Medusa'

        if not app.USE_NMA and not force:
            return False

        if nma_api is None:
            nma_api = app.NMA_API
        else:
            nma_api = nma_api.split(',')

        if nma_priority is None:
            nma_priority = app.NMA_PRIORITY

        batch = False

        p = pynma.PyNMA()
        keys = nma_api
        p.addkey(keys)

        if len(keys) > 1:
            batch = True

        log.debug(u'NMA: Sending notice with details: event="{0}, message="{1}", priority={2}, batch={3}',
                  event, message, nma_priority, batch)
        response = p.push(application=title, event=event, description=message, priority=nma_priority, batch_mode=batch)

        if not response[nma_api][u'code'] == u'200':
            log.error(u'Could not send notification to NotifyMyAndroid')
            return False
        else:
            log.info(u'NMA: Notification sent to NotifyMyAndroid')
            return True