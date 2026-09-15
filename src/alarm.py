class Alarm:
    def __init__(self):
        self.active = False

    def update(self, state):
        if state == "IN BED":
            self.active = True
        elif state == "OUT OF BED":
            self.active = False

        return self.active
    
    def getState(self):
        return self.active