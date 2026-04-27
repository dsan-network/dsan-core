from dsan.core.state import DSANState

def replay_ledger(ledger):
    state = DSANState()

    for entry in ledger:
        state.apply(entry["event"])

    return state.root()