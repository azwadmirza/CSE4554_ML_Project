    def is_best_loss(results, current_best_loss) -> bool:
        return results['loss'] < current_best_loss