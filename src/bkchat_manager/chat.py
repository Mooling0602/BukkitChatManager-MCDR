from uuid import UUID

from auto_uuid_api import local_api
from mcdreforged import RHoverEntity, RText


def get_player_entity(player: str) -> RHoverEntity:
    uuid = local_api.get_uuid(player)
    if not uuid:
        raise ValueError(f"Player {player}'s UUID is not found")
    return RHoverEntity("minecraft:player", UUID(uuid), player)


def get_player_rtext(player: str | RHoverEntity) -> RText:
    if isinstance(player, str):
        player = get_player_entity(player)
    return RText(player.name).set_hover_text(player)
