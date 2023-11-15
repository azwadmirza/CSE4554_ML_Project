    def send_vip_object(self, message):
        """
        Send the VIP message over RabbitMQ message bus.
        Reformat the VIP message object into Pika message object and
        publish it using Pika library
        :param message: VIP message object
        :return:
        """
        platform = getattr(message, 'platform', self._instance_name)
        if message.peer == b'':
            message.peer = 'router'
        if platform == b'':
            platform = self._instance_name

        destination_routing_key = "{0}.{1}".format(platform, message.peer)

        # Fit VIP frames in the PIKA properties dict
        # VIP format - [SENDER, RECIPIENT, PROTO, USER_ID, MSG_ID, SUBSYS, ARGS...]
        dct = {
            'user_id': self._rmq_userid,
            'app_id': self.routing_key,  # Routing key of SENDER
            'headers': dict(
                            recipient=destination_routing_key,  # RECEIVER
                            proto=b'VIP',  # PROTO
                            user=getattr(message, 'user', self._rmq_userid),  # USER_ID
                            ),
            'message_id': getattr(message, 'id', b''),  # MSG_ID
            'type': message.subsystem,  # SUBSYS
            'content_type': 'application/json'
        }
        properties = pika.BasicProperties(**dct)
        msg = getattr(message, 'args', None)  # ARGS
        # _log.debug("PUBLISHING TO CHANNEL {0}, {1}, {2}, {3}".format(destination_routing_key,
        #                                                              msg,
        #                                                              properties,
        #                                                              self.routing_key))
        try:
            self.channel.basic_publish(self.exchange,
                                   destination_routing_key,
                                   json.dumps(msg, ensure_ascii=False),
                                   properties)
        except (pika.exceptions.AMQPConnectionErro,
                pika.exceptions.AMQPChannelError) as exc:
            raise Unreachable(errno.EHOSTUNREACH, "Connection to RabbitMQ is lost",
                              'rabbitmq broker', 'rmq_connection')