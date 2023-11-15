def watch(limit):
    """watch scan rates across the cluster"""
    period = 5.0
    prev = db.db()
    prev_totals = None

    while True:
        click.clear()
        time.sleep(period)
        cur = db.db()
        cur.data['gkrate'] = {}
        progress = []
        prev_buckets = {b.bucket_id: b for b in prev.buckets()}

        totals = {'scanned': 0, 'krate': 0, 'lrate': 0, 'bucket_id': 'totals'}

        for b in cur.buckets():
            if not b.scanned:
                continue

            totals['scanned'] += b.scanned
            totals['krate'] += b.krate
            totals['lrate'] += b.lrate

            if b.bucket_id not in prev_buckets:
                b.data['gkrate'][b.bucket_id] = b.scanned / period
            elif b.scanned == prev_buckets[b.bucket_id].scanned:
                continue
            else:
                b.data['gkrate'][b.bucket_id] = (
                    b.scanned - prev_buckets[b.bucket_id].scanned) / period
            progress.append(b)

        if prev_totals is None:
            totals['gkrate'] = '...'
        else:
            totals['gkrate'] = (totals['scanned'] - prev_totals['scanned']) / period
        prev = cur
        prev_totals = totals

        progress = sorted(progress, key=lambda x: x.gkrate, reverse=True)

        if limit:
            progress = progress[:limit]

        progress.insert(0, Bag(totals))
        format_plain(
            progress, None,
            explicit_only=True,
            keys=['bucket_id', 'scanned', 'gkrate', 'lrate', 'krate'])