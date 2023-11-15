    def _run_job(self, job_id, qobj):
        """Run a Qobj on the backend."""
        self._validate(qobj)
        final_state_key = 32767  # Internal key for final state snapshot
        # Add final snapshots to circuits
        for experiment in qobj.experiments:
            experiment.instructions.append(
                QobjInstruction(name='snapshot', params=[final_state_key])
            )
        result = super()._run_job(job_id, qobj)
        # Replace backend name with current backend
        result.backend_name = self.name
        # Extract final state snapshot and move to 'statevector' data field
        for experiment_result in result.results.values():
            snapshots = experiment_result.snapshots
            if str(final_state_key) in snapshots:
                final_state_key = str(final_state_key)
            # Pop off final snapshot added above
            final_state = snapshots.pop(final_state_key, None)
            final_state = final_state['statevector'][0]
            # Add final state to results data
            experiment_result.data['statevector'] = final_state
            # Remove snapshot dict if empty
            if snapshots == {}:
                experiment_result.data.pop('snapshots', None)
        return result