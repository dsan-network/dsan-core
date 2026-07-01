from dsan.core.state import DSANState


def replay_ledger(ledger):
    state = DSANState()

    for entry in ledger:
        event = entry["event"]
        state.apply(event)

    return state.root()