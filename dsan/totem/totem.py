class DSANTotem:
    def __init__(self):
        self.unlock_sequence = [1, 2, 0]

    def authorize(self):
        try:
            raw = input("🔐 Totem gesture (ex: 120): ")
            seq = [int(x) for x in raw]
            return seq == self.unlock_sequence
        except:
            return False