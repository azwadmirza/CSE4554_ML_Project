def encode(var):
    return CFTimedeltaCoder().encode(CFDatetimeCoder().encode(var.variable))