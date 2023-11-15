    def get_docker_memory(self, container_id, all_stats):
        """Return the container MEMORY.

        Input: id is the full container id
               all_stats is the output of the stats method of the Docker API
        Output: a dict {'rss': 1015808, 'cache': 356352,  'usage': ..., 'max_usage': ...}
        """
        ret = {}
        # Read the stats
        try:
            # Do not exist anymore with Docker 1.11 (issue #848)
            # ret['rss'] = all_stats['memory_stats']['stats']['rss']
            # ret['cache'] = all_stats['memory_stats']['stats']['cache']
            ret['usage'] = all_stats['memory_stats']['usage']
            ret['limit'] = all_stats['memory_stats']['limit']
            ret['max_usage'] = all_stats['memory_stats']['max_usage']
        except (KeyError, TypeError) as e:
            # all_stats do not have MEM information
            logger.debug("Can not grab MEM usage for container {0} ({1})".format(container_id, e))
            logger.debug(all_stats)
        # Return the stats
        return ret