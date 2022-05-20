def confGetOrDefault (conf, key, default=None, cast=lambda y: y):
    def iteOver(c, k):
        if len(k) == 1:
            return cast(c[k[0]]) if k[0] in c else default
        else:
            ke = k[0]
            k = k[1:]
            return iteOver (c[ke], k) if ke in conf else default
            
    if type(key) == str:
        key = key.split('.')

    return iteOver(conf, key)