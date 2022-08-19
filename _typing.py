import sys

if sys.version_info < (3, 8):
    from typing_extensions import Literal, TypedDict
else:
    from typing import Literal, TypedDict


# Valid transaction broadcast modes for the `POST /txs` endpoint of the
# Cyber REST API.
SyncMode = Literal["broadcast_tx_sync", "broadcast_tx_async", "broadcast_tx_commit"]


class Wallet(TypedDict):
    seed: str
    derivation_path: str
    private_key: bytes
    public_key: bytes
    address: str
