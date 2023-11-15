    def is_flapping(self, alert, window=1800, count=2):
        """
        Return true if alert severity has changed more than X times in Y seconds
        """
        pipeline = [
            {'$match': {
                "environment": alert.environment,
                "resource": alert.resource,
                "event": alert.event,
                "customer": alert.customer
            }},
            {'$unwind': '$history'},
            {'$match': {
                "history.updateTime": {'$gt': datetime.utcnow() - timedelta(seconds=window)},
                "history.type": "severity"
            }},
            {'$group': {"_id": '$history.type', "count": {'$sum': 1}}}
        ]
        responses = g.db.alerts.aggregate(pipeline)
        for r in responses:
            if r['count'] > count:
                return True
        return False