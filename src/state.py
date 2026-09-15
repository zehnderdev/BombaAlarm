import time

class BedState:
    def __init__(self, duration=10, threshold=0.8):
        self.duration = duration
        self.threshold = threshold
        self.history = []

    def update(self, in_bed):
        now = time.monotonic()

        self.history.append((now, in_bed))

        # remove old entries
        self.history = [
            (timestamp, state)
            for timestamp, state in self.history
            if now - timestamp <= self.duration
        ]
        if not self.history:
            return "UNKNOWN"

        in_bed_count = sum(state for _, state in self.history)
        ratio = in_bed_count / len(self.history)

        if ratio >= self.threshold:
            return "IN BED"

        return "OUT OF BED"

    def getState(self):
        in_bed_count = sum(state for _, state in self.history)
        ratio = in_bed_count / len(self.history)

        if ratio >= self.threshold:
            return "IN BED"
        
        return "OUT OF BED"