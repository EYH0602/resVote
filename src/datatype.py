from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime
from .util import to_vote_id


@dataclass
class Vote:
    election_id: str
    candidate_name: str
    voter_id: str

    # transfer datetime to json format
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_real: bool = True

    @property
    def transaction_id(self):
        return to_vote_id(self.election_id, self.voter_id)


@dataclass
class Election:
    election_id: str
    candidates: list[str]
    creator: str

    @property
    def transaction_id(self):
        return self.election_id


@dataclass
class Voter:
    voter_id: str
    password: str

    age: int = 20
    gender: str = "male"
    region: str = "unknown"
    race: str = "unknown"
    education: str = "unknown"
    is_real: bool = True
    is_admin: bool = False

    @property
    def transaction_id(self) -> str:
        return self.voter_id
