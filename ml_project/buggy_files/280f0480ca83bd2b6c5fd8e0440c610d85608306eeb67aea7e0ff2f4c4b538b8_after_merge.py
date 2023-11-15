    def _receive_packet(self, packet: dict):
        name = packet['name']
        if name == 'ping':
            self.ping_packet(packet['when'])
        elif name == 'get-current-submission':
            self.current_submission_packet()
        elif name == 'submission-request':
            self.submission_acknowledged_packet(packet['submission-id'])
            from dmoj.judge import Submission

            self.judge.begin_grading(
                Submission(
                    id=packet['submission-id'],
                    problem_id=packet['problem-id'],
                    language=packet['language'],
                    source=packet['source'],
                    time_limit=float(packet['time-limit']),
                    memory_limit=int(packet['memory-limit']),
                    short_circuit=packet['short-circuit'],
                    meta=packet['meta'],
                )
            )
            self._batch = 0
            log.info(
                'Accept submission: %d: executor: %s, code: %s',
                packet['submission-id'],
                packet['language'],
                packet['problem-id'],
            )
        elif name == 'terminate-submission':
            self.judge.abort_grading()
        elif name == 'disconnect':
            log.info('Received disconnect request, shutting down...')
            self.disconnect()
        else:
            log.error('Unknown packet %s, payload %s', name, packet)