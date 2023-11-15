    def _initialize_global_state(self, redis_ip_address, redis_port):
        """Initialize the GlobalState object by connecting to Redis.

        Args:
            redis_ip_address: The IP address of the node that the Redis server
                lives on.
            redis_port: The port that the Redis server is listening on.
        """
        self.redis_client = redis.StrictRedis(host=redis_ip_address,
                                              port=redis_port)
        self.redis_clients = []
        num_redis_shards = self.redis_client.get("NumRedisShards")
        if num_redis_shards is None:
            raise Exception("No entry found for NumRedisShards")
        num_redis_shards = int(num_redis_shards)
        if (num_redis_shards < 1):
            raise Exception("Expected at least one Redis shard, found "
                            "{}.".format(num_redis_shards))

        ip_address_ports = self.redis_client.lrange("RedisShards", start=0,
                                                    end=-1)
        if len(ip_address_ports) != num_redis_shards:
            raise Exception("Expected {} Redis shard addresses, found "
                            "{}".format(num_redis_shards,
                                        len(ip_address_ports)))

        for ip_address_port in ip_address_ports:
            shard_address, shard_port = ip_address_port.split(b":")
            self.redis_clients.append(redis.StrictRedis(host=shard_address,
                                                        port=shard_port))