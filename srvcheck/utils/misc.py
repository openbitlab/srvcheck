def confGetOrDefault (conf, key, default=None):
    def iteOver(c, k):
        if len(k) == 1:
            out = c[k] if k in c else default
            return out if out.isdigit() == False else int(out)
        else:
            ke = k[0]
            k = k[1:]
            return iteOver (c[ke], k) if ke in conf else default
            
    if type(key) == str:
        key = key.split('.')

    return iteOver(conf, key)