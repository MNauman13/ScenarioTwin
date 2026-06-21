from __future__ import annotations

import hashlib
import json

import redis

from .config import settings

_redis: redis.Redis = redis.from_url(settings.redis_url, decode_responses=True)
_TTL = 3600  # 1 hour


def _make_key(profile_id: int, scenario: dict) -> str:
    raw = f"{profile_id}:{json.dumps(scenario, sort_keys=True)}"
    return "sim:" + hashlib.sha256(raw.encode()).hexdigest()


def get(profile_id: int, scenario: dict) -> dict | None:
    value = _redis.get(_make_key(profile_id, scenario))
    return json.loads(value) if value else None


def set(profile_id: int, scenario: dict, result: dict) -> None:
    _redis.setex(_make_key(profile_id, scenario), _TTL, json.dumps(result))
