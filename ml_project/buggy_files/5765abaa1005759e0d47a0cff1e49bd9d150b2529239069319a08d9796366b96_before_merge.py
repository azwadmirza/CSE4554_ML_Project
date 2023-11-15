    def housekeeping(self, expired_threshold, info_threshold):
        # delete 'closed' or 'expired' alerts older than "expired_threshold" hours
        # and 'informational' alerts older than "info_threshold" hours
        expired_hours_ago = datetime.utcnow() - timedelta(hours=expired_threshold)
        g.db.alerts.remove({"status": {'$in': ["closed", "expired"]}, "lastReceiveTime": {'$lt': expired_hours_ago}})

        info_hours_ago = datetime.utcnow() - timedelta(hours=info_threshold)
        g.db.alerts.remove({"severity": "informational", "lastReceiveTime": {'$lt': info_hours_ago}})

        # get list of alerts to be newly expired
        pipeline = [
            {'$project': {
                "event": 1, "status": 1, "lastReceiveId": 1, "timeout": 1,
                "expireTime": {'$add': ["$lastReceiveTime", {'$multiply': ["$timeout", 1000]}]}}
            },
            {'$match': {"status": {'$nin': ['expired', 'shelved']}, "expireTime": {'$lt': datetime.utcnow()}, "timeout": {'$ne': 0}}}
        ]
        expired = [(r['_id'], r['event'], 'expired', r['lastReceiveId']) for r in g.db.alerts.aggregate(pipeline)]

        # get list of alerts to be unshelved
        pipeline = [
            {'$project': {
                "event": 1, "status": 1, "lastReceiveId": 1, "timeout": 1,
                "expireTime": {'$add': ["$lastReceiveTime", {'$multiply': ["$timeout", 1000]}]}}
            },
            {'$match': {"status": 'shelved', "expireTime": {'$lt': datetime.utcnow()}, "timeout": {'$ne': 0}}}
        ]
        unshelved = [(r['_id'], r['event'], 'open', r['lastReceiveId']) for r in g.db.alerts.aggregate(pipeline)]

        return expired + unshelved