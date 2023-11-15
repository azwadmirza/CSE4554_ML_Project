  def process_call(self, call_primitive, f: lu.WrappedFun, tracers, params):
    # TODO apply proper subtrace:
    return map(self.full_raise, f.call_wrapped(*tracers))