"""Functions related to player actions in the labyrinth game."""

from labyrinth_game.constants import ROOMS
from labyrinth_game.utils import describe_current_room, random_event


def show_inventory(game_state: dict) -> None:
    """Print the player's inventory or a message if it is empty."""
    inventory = game_state.get("player_inventory", [])

    if not inventory:
        print("Ваш инвентарь пуст.")
        return

    items_list = ", ".join(inventory)
    print(f"В вашем инвентаре: {items_list}")


def get_input(prompt: str = "> ") -> str:
    """Get user input, handling basic interruption errors."""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def move_player(game_state: dict, direction: str) -> None:
    """Move the player to another room if possible."""
    current_room_key = game_state.get("current_room")
    room = ROOMS.get(current_room_key, {})

    exits = room.get("exits", {})
    target_room = exits.get(direction.lower())

    if not target_room:
        print("Нельзя пойти в этом направлении.")
        return

    # Особая проверка для комнаты с сокровищами.
    if target_room == "treasure_room":
        inventory = game_state.get("player_inventory", [])
        if not any(
            item.lower().replace(" ", "_") == "rusty_key" for item in inventory
        ):
            print("Дверь заперта. Нужен ключ, чтобы пройти дальше.")
            return

        print("Вы используете найденный ключ, чтобы открыть путь в комнату сокровищ.")

    game_state["current_room"] = target_room
    game_state["steps_taken"] = game_state.get("steps_taken", 0) + 1
    describe_current_room(game_state)
    random_event(game_state)


def _find_item_in_inventory(game_state: dict, item_name: str) -> str | None:
    """Return the canonical item name from inventory matching the given name."""
    inventory = game_state.get("player_inventory", [])
    normalized = item_name.lower().replace(" ", "_")

    for item in inventory:
        if item.lower().replace(" ", "_") == normalized:
            return item
    return None


def take_item(game_state: dict, item_name: str) -> None:
    """Take an item from the current room and add it to the player's inventory."""
    current_room_key = game_state.get("current_room")
    room = ROOMS.get(current_room_key, {})

    items = room.get("items", [])
    normalized = item_name.lower().replace(" ", "_")

    # Нельзя поднять сундук.
    if normalized in {"treasure_chest", "treasure-chest"}:
        print("Вы не можете поднять сундук, он слишком тяжелый.")
        return

    # Найти совпадающий предмет по имени (с учётом возможного пробела/подчёркивания).
    found_item = None
    for item in items:
        if item.lower().replace(" ", "_") == normalized:
            found_item = item
            break

    if not found_item:
        print("Такого предмета здесь нет.")
        return

    items.remove(found_item)
    inventory = game_state.setdefault("player_inventory", [])
    inventory.append(found_item)
    print(f"Вы подняли: {found_item}")


def use_item(game_state: dict, item_name: str) -> None:
    """Use an item from the player's inventory."""
    stored_name = _find_item_in_inventory(game_state, item_name)

    if stored_name is None:
        print("У вас нет такого предмета.")
        return

    normalized = stored_name.lower().replace(" ", "_")

    if normalized == "torch":
        print("Вы зажигаете факел. Вокруг становится светлее.")
    elif normalized == "sword":
        print("Вы крепче сжимаете меч и чувствуете прилив уверенности.")
    elif normalized == "bronze_box":
        print("Вы открываете бронзовую шкатулку.")
        inventory = game_state.setdefault("player_inventory", [])
        if not any(
            item.lower().replace(" ", "_") == "rusty_key" for item in inventory
        ):
            inventory.append("rusty_key")
            print("Внутри вы находите ржавый ключ и кладёте его в инвентарь.")
    else:
        print("Вы не уверены, как использовать этот предмет.")


