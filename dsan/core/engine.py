class DSANEngine:
    def __init__(self):
        self.allowed_actions = {
            "transfer_funds": self.transfer,
            "test": self.test
        }

    def execute(self, action):
        if action not in self.allowed_actions:
            raise Exception("Action not allowed")

        return self.allowed_actions[action]()

    def transfer(self):
        return "[TRANSFER EXECUTED]"

    def test(self):
        return "[TEST OK]"