class DSANPolicy:

    @staticmethod
    def evaluate(event):
        payload = event["payload"]

        # regra 1: transfer precisa de totem
        if payload.get("msg") == "transfer_funds":
            return {
                "allowed": True,
                "require_totem": True
            }

        # regra padrão
        return {
            "allowed": True,
            "require_totem": False
        }