class ExecutionContext:
    def __init__(self, peers):
        if not peers:
            self.mode = "OFFLINE"
        else:
            self.mode = "HYBRID"

    def is_offline(self):
        return self.mode == "OFFLINE"

    def is_hybrid(self):
        return self.mode == "HYBRID"