from api.infra.redis import get_redis

def add_jti_to_blocklist(jti: str, exp: int):
    get_redis().setex(f"blocklist:{jti}", exp, "true")

def is_jti_blocked(jti: str) -> bool:
    return get_redis().exists(f"blocklist:{jti}") == 1