def _get_dummy_effects(effects, exog, dummy_ind, method, model, params):
    for i, tf in enumerate(dummy_ind):
        if tf == True:
            exog0 = exog.copy() # only copy once, can we avoid a copy?
            exog0[:,i] = 0
            effect0 = model.predict(params, exog0)
            #fittedvalues0 = np.dot(exog0,params)
            exog0[:,i] = 1
            effect1 = model.predict(params, exog0)
            if 'ey' in method:
                effect0 = np.log(effect0)
                effect1 = np.log(effect1)
            effects[i] = (effect1 - effect0).mean() # mean for overall
    return effects