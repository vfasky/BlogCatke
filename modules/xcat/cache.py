#coding=utf-8
import os
if 'SERVER_SOFTWARE' in os.environ:
    import pylibmc


class Static(object):
    """静态变量缓存"""

    data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

class SaePylibmc(object):
    """基于 sae MC 的缓存"""

    mc = False
    if 'SERVER_SOFTWARE' in os.environ:
        mc = pylibmc.Client()

    def get(self, key, default=None):
        ret = self.mc.get(key)
        if not ret:
            return default
        return ret

    def set(self, key, value):
        self.mc.set(key, value)


client = Static()
        
