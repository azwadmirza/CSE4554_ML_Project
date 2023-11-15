    def processSubscribe(self, session, subscribe):
        """
        Implements :func:`crossbar.router.interfaces.IBroker.processSubscribe`
        """
        if self._router.is_traced:
            if not subscribe.correlation_id:
                subscribe.correlation_id = self._router.new_correlation_id()
                subscribe.correlation_is_anchor = True
                subscribe.correlation_is_last = False
            if not subscribe.correlation_uri:
                subscribe.correlation_uri = subscribe.topic
            self._router._factory._worker._maybe_trace_rx_msg(session, subscribe)

        # check topic URI: for SUBSCRIBE, must be valid URI (either strict or loose), and all
        # URI components must be non-empty for normal subscriptions, may be empty for
        # wildcard subscriptions and must be non-empty for all but the last component for
        # prefix subscriptions
        #
        if self._option_uri_strict:
            if subscribe.match == u"wildcard":
                uri_is_valid = _URI_PAT_STRICT_EMPTY.match(subscribe.topic)
            elif subscribe.match == u"prefix":
                uri_is_valid = _URI_PAT_STRICT_LAST_EMPTY.match(subscribe.topic)
            else:
                uri_is_valid = _URI_PAT_STRICT_NON_EMPTY.match(subscribe.topic)
        else:
            if subscribe.match == u"wildcard":
                uri_is_valid = _URI_PAT_LOOSE_EMPTY.match(subscribe.topic)
            elif subscribe.match == u"prefix":
                uri_is_valid = _URI_PAT_LOOSE_LAST_EMPTY.match(subscribe.topic)
            else:
                uri_is_valid = _URI_PAT_LOOSE_NON_EMPTY.match(subscribe.topic)

        if not uri_is_valid:
            reply = message.Error(message.Subscribe.MESSAGE_TYPE, subscribe.request, ApplicationError.INVALID_URI, [u"subscribe for invalid topic URI '{0}'".format(subscribe.topic)])
            reply.correlation_id = subscribe.correlation_id
            reply.correlation_uri = subscribe.topic
            reply.correlation_is_anchor = False
            reply.correlation_is_last = True
            self._router.send(session, reply)
            return

        # authorize SUBSCRIBE action
        #
        d = self._router.authorize(session, subscribe.topic, u'subscribe', options=subscribe.marshal_options())

        def on_authorize_success(authorization):
            if not authorization[u'allow']:
                # error reply since session is not authorized to subscribe
                #
                replies = [message.Error(message.Subscribe.MESSAGE_TYPE, subscribe.request, ApplicationError.NOT_AUTHORIZED, [u"session is not authorized to subscribe to topic '{0}'".format(subscribe.topic)])]
                replies[0].correlation_id = subscribe.correlation_id
                replies[0].correlation_uri = subscribe.topic
                replies[0].correlation_is_anchor = False
                replies[0].correlation_is_last = True

            else:
                # ok, session authorized to subscribe. now get the subscription
                #
                subscription, was_already_subscribed, is_first_subscriber = self._subscription_map.add_observer(session, subscribe.topic, subscribe.match, extra=SubscriptionExtra())

                if not was_already_subscribed:
                    self._session_to_subscriptions[session].add(subscription)

                # publish WAMP meta events, if we have a service session, but
                # not for the meta API itself!
                #
                if self._router._realm and \
                   self._router._realm.session and \
                   not subscription.uri.startswith(u'wamp.') and \
                   (is_first_subscriber or not was_already_subscribed):

                    has_follow_up_messages = True

                    exclude_authid = None
                    if subscribe.forward_for:
                        exclude_authid = [ff['authid'] for ff in subscribe.forward_for]

                    def _publish():
                        service_session = self._router._realm.session

                        if exclude_authid or self._router.is_traced:
                            options = types.PublishOptions(
                                correlation_id=subscribe.correlation_id,
                                correlation_is_anchor=False,
                                correlation_is_last=False,
                                exclude_authid=exclude_authid,
                            )
                        else:
                            options = None

                        if is_first_subscriber:
                            subscription_details = {
                                u'id': subscription.id,
                                u'created': subscription.created,
                                u'uri': subscription.uri,
                                u'match': subscription.match,
                            }
                            service_session.publish(
                                u'wamp.subscription.on_create',
                                session._session_id,
                                subscription_details,
                                options=options,
                            )

                        if not was_already_subscribed:
                            if options:
                                options.correlation_is_last = True

                            service_session.publish(
                                u'wamp.subscription.on_subscribe',
                                session._session_id,
                                subscription.id,
                                options=options,
                            )
                    # we postpone actual sending of meta events until we return to this client session
                    self._reactor.callLater(0, _publish)

                else:
                    has_follow_up_messages = False

                # check for retained events
                #
                def _get_retained_event():

                    if subscription.extra.retained_events:
                        retained_events = list(subscription.extra.retained_events)
                        retained_events.reverse()

                        for retained_event in retained_events:
                            authorized = False

                            if not retained_event.publish.exclude and not retained_event.publish.eligible:
                                authorized = True
                            elif session._session_id in retained_event.publish.eligible and session._session_id not in retained_event.publish.exclude:
                                authorized = True

                            if authorized:
                                publication = util.id()

                                if retained_event.publish.payload:
                                    msg = message.Event(subscription.id,
                                                        publication,
                                                        payload=retained_event.publish.payload,
                                                        enc_algo=retained_event.publish.enc_algo,
                                                        enc_key=retained_event.publish.enc_key,
                                                        enc_serializer=retained_event.publish.enc_serializer,
                                                        publisher=retained_event.publisher,
                                                        publisher_authid=retained_event.publisher_authid,
                                                        publisher_authrole=retained_event.publisher_authrole,
                                                        retained=True)
                                else:
                                    msg = message.Event(subscription.id,
                                                        publication,
                                                        args=retained_event.publish.args,
                                                        kwargs=retained_event.publish.kwargs,
                                                        publisher=retained_event.publisher,
                                                        publisher_authid=retained_event.publisher_authid,
                                                        publisher_authrole=retained_event.publisher_authrole,
                                                        retained=True)

                                msg.correlation_id = subscribe.correlation_id
                                msg.correlation_uri = subscribe.topic
                                msg.correlation_is_anchor = False
                                msg.correlation_is_last = False

                                return [msg]
                    return []

                # acknowledge subscribe with subscription ID
                #
                replies = [message.Subscribed(subscribe.request, subscription.id)]
                replies[0].correlation_id = subscribe.correlation_id
                replies[0].correlation_uri = subscribe.topic
                replies[0].correlation_is_anchor = False
                replies[0].correlation_is_last = False
                if subscribe.get_retained:
                    replies.extend(_get_retained_event())

                replies[-1].correlation_is_last = not has_follow_up_messages

            # send out reply to subscribe requestor
            #
            [self._router.send(session, reply) for reply in replies]

        def on_authorize_error(err):
            """
            the call to authorize the action _itself_ failed (note this is
            different from the call to authorize succeed, but the
            authorization being denied)
            """
            self.log.failure("Authorization of 'subscribe' for '{uri}' failed",
                             uri=subscribe.topic, failure=err)
            reply = message.Error(
                message.Subscribe.MESSAGE_TYPE,
                subscribe.request,
                ApplicationError.AUTHORIZATION_FAILED,
                [u"failed to authorize session for subscribing to topic URI '{0}': {1}".format(subscribe.topic, err.value)]
            )
            reply.correlation_id = subscribe.correlation_id
            reply.correlation_uri = subscribe.topic
            reply.correlation_is_anchor = False
            reply.correlation_is_last = True
            self._router.send(session, reply)

        txaio.add_callbacks(d, on_authorize_success, on_authorize_error)