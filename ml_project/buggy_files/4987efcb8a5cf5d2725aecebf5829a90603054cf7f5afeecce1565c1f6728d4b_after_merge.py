    def _initialize_global_state(self, redis_ip_address, redis_port,
                                 timeout=20):
        """Initialize the GlobalState object by connecting to Redis.

        It's possible that certain keys in Redis may not have been fully
        populated yet. In this case, we will retry this method until they have
        been populated or we exceed a timeout.

        Args:
            redis_ip_address: The IP address of the node that the Redis server
                lives on.
            redis_port: The port that the Redis server is listening on.
            timeout: The maximum amount of time (in seconds) that we should
                wait for the keys in Redis to be populated.
        """
        self.redis_client = redis.StrictRedis(host=redis_ip_address,
                                              port=redis_port)

        start_time = time.time()

        num_redis_shards = None
        ip_address_ports = []

        while time.time() - start_time < timeout:
            # Attempt to get the number of Redis shards.
            num_redis_shards = self.redis_client.get("NumRedisShards")
            if num_redis_shards is None:
                print("Waiting longer for NumRedisShards to be populated.")
                time.sleep(1)
                continue
            num_redis_shards = int(num_redis_shards)
            if (num_redis_shards < 1):
                raise Exception("Expected at least one Redis shard, found "
                                "{}.".format(num_redis_shards))

            # Attempt to get all of the Redis shards.
            ip_address_ports = self.redis_client.lrange("RedisShards", start=0,
                                                        end=-1)
            if len(ip_address_ports) != num_redis_shards:
                print("Waiting longer for RedisShards to be populated.")
                time.sleep(1)
                continue

            # If we got here then we successfully got all of the information.
            break

        # Check to see if we timed out.
        if time.time() - start_time >= timeout:
            raise Exception("Timed out while attempting to initialize the "
                            "global state. num_redis_shards = {}, "
                            "ip_address_ports = {}"
                            .format(num_redis_shards, ip_address_ports))

        # Get the rest of the information.
        self.redis_clients = []
        for ip_address_port in ip_address_ports:
            shard_address, shard_port = ip_address_port.split(b":")
            self.redis_clients.append(redis.StrictRedis(host=shard_address,
                                                        port=shard_port))