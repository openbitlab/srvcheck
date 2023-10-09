import urllib.parse


class NotificationProvider:
    def __init__(self, conf):
        self.conf = conf
        self.notifies = []

    def __del__(self):
        self.flush()

    def send(self, st, level):
        raise Exception("Abstract send()")

    def sendPhoto(self, photo, level):
        pass

    def append(self, s, level):
        self.notifies.append((s, level))

    def format(self, name, string):
        return urllib.parse.quote("#" + name + " " + string)

    def flush(self):
        if len(self.notifies) > 0:
            levelGroups = {}
            for s, level in self.notifies:
                if level not in levelGroups:
                    levelGroups[level] = []
                levelGroups[level].append(s)

            for level in levelGroups.keys():
                st = "\n".join(levelGroups[level])
                self.send(self.format(st, ""), level)

            self.notifies = []
