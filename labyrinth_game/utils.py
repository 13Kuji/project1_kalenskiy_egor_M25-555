"""Utility functions for the labyrinth game."""

import math

from labyrinth_game.constants import (
    COMMANDS,
    EVENT_PROBABILITY,
    EVENT_TRIGGER_VALUE,
    EVENT_TYPE_COUNT,
    EVENT_TYPE_FIND,
    EVENT_TYPE_SCARE,
    ROOMS,
    TRAP_DAMAGE_ROLL_MODULO,
    TRAP_DEATH_THRESHOLD,
)


def _get_input(prompt: str) -> str:
    """Get user input, handling interruption errors."""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"


def _normalize_answer(text: str) -> str:
    """Normalize user and correct answers for comparison."""
    return str(text).strip().lower()


def describe_current_room(game_state: dict) -> None:
    """Print a description of the current room based on the game state."""
    room_key = game_state.get("current_room")
    room = ROOMS.get(room_key)

    if room is None:
        print("Неизвестная комната. Что-то пошло не так...")
        return

    # Название комнаты
    print(f"== {room_key.upper()} ==")

    # Описание комнаты
    print(room["description"])

    # Предметы в комнате
    items = room.get("items", [])
    if items:
        items_list = ", ".join(items)
        print(f"Заметные предметы: {items_list}")

    # Доступные выходы
    exits = room.get("exits", {})
    if exits:
        exits_list = ", ".join(
            f"{direction} -> {target}" for direction, target in exits.items()
        )
        print(f"Выходы: {exits_list}")

    # Наличие загадки
    if room.get("puzzle") is not None:
        print("Кажется, здесь есть загадка (используйте команду solve).")


def pseudo_random(seed: int, modulo: int) -> int:
    """Deterministic pseudo-random integer in [0, modulo) based on math.sin.

    The result depends only on the given seed and modulo and does not use
    the standard `random` module.
    """
    if modulo <= 0:
        return 0

    x = math.sin(seed * 12.9898) * 43758.5453
    frac = x - math.floor(x)
    value = int(math.floor(frac * modulo))
    # На всякий случай нормализуем результат в нужный диапазон.
    return max(0, min(modulo - 1, value))


def trigger_trap(game_state: dict) -> None:
    """Simulate a trap being triggered with negative consequences."""
    print("Ловушка активирована! Пол начинает дрожать...")

    inventory = game_state.setdefault("player_inventory", [])

    # Если что-то есть в инвентаре — теряем случайный предмет.
    if inventory:
        index = pseudo_random(game_state.get("steps_taken", 0), len(inventory))
        lost_item = inventory.pop(index)
        print(f"Вы теряете предмет: {lost_item}!")
        return

    # Иначе — потенциальный урон для игрока.
    roll = pseudo_random(
        game_state.get("steps_taken", 0), TRAP_DAMAGE_ROLL_MODULO
    )
    if roll < TRAP_DEATH_THRESHOLD:
        print("Ловушка срабатывает смертельно. Вы не успеваете спастись...")
        game_state["game_over"] = True
    else:
        print("Вы чудом избегаете серьёзных повреждений.")


def show_help(commands: dict[str, str] | None = None) -> None:
    """Show help for available commands."""
    print("\nДоступные команды:")
    mapping = commands or COMMANDS
    for name, description in mapping.items():
        print(f"  {name:<16} - {description}")


def solve_puzzle(game_state: dict) -> None:
    """Try to solve a puzzle in the current room."""
    room_key = game_state.get("current_room")
    room = ROOMS.get(room_key, {})

    puzzle = room.get("puzzle")
    if not puzzle:
        print("Загадок здесь нет.")
        return

    question, answer = puzzle
    print(question)
    user_answer = _get_input("Ваш ответ: ").strip()

    user_norm = _normalize_answer(user_answer)
    correct_norm = _normalize_answer(answer)

    is_correct = False
    # Поддерживаем альтернативные варианты ответа для чисел, например "10"/"десять".
    if correct_norm == "10" and user_norm in {"10", "десять"}:
        is_correct = True
    elif user_norm == correct_norm:
        is_correct = True

    if is_correct:
        print("Верно! Вы успешно решили загадку.")
        # Убираем загадку, чтобы её нельзя было решить второй раз.
        room["puzzle"] = None

        # Награда зависит от комнаты.
        inventory = game_state.setdefault("player_inventory", [])
        if room_key == "hall":
            reward = "treasure_key"
            if reward not in inventory:
                inventory.append(reward)
                print("Вы получаете сокровищный ключ!")
        elif room_key == "library":
            reward = "ancient_hint"
            inventory.append(reward)
            print("Вы находите древнюю подсказку среди свитков.")
        elif room_key == "trap_room":
            reward = "trap_token"
            inventory.append(reward)
            print("Вы успешно обходите ловушки и находите странный знак.")
        else:
            reward = "mysterious_token"
            inventory.append(reward)
            print("Вы получаете таинственный символ как награду.")
    else:
        print("Неверно. Попробуйте снова.")
        if room_key == "trap_room":
            trigger_trap(game_state)


def attempt_open_treasure(game_state: dict) -> None:
    """Try to open the treasure chest using a key or by entering a code."""
    room_key = game_state.get("current_room")
    if room_key != "treasure_room":
        print("Здесь нечего открывать.")
        return

    room = ROOMS.get(room_key, {})
    items = room.get("items", [])
    if "treasure_chest" not in items:
        print("Сундук уже открыт.")
        return

    inventory = game_state.setdefault("player_inventory", [])

    # 1. Попытка использовать ключ.
    if "treasure_key" in inventory:
        print("Вы применяете ключ, и замок щёлкает. Сундук открыт!")
        items.remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
        return

    # 2. Попытка взломать кодом.
    print(
        "Сундук заперт. Похоже, его можно открыть, если ввести правильный код.",
    )
    choice = _get_input("Ввести код? (да/нет): ").strip().lower()

    if choice not in {"да", "yes", "y"}:
        print("Вы отступаете от сундука.")
        return

    puzzle = room.get("puzzle")
    if not puzzle:
        print("Кажется, здесь нет кода для сундука.")
        return

    _, answer = puzzle
    code = _get_input("Введите код: ").strip()

    if code.lower() == str(answer).lower():
        print("Код верный! Замок щёлкает, и сундук открывается.")
        items.remove("treasure_chest")
        print("В сундуке сокровище! Вы победили!")
        game_state["game_over"] = True
    else:
        print("Код неверный. Сундук остаётся заперт.")


def random_event(game_state: dict) -> None:
    """Trigger small random events during movement."""
    seed = game_state.get("steps_taken", 0)

    # Сначала определяем, произойдёт ли событие вообще.
    # Вероятность низкая: событие только если результат равен EVENT_TRIGGER_VALUE.
    if pseudo_random(seed, EVENT_PROBABILITY) != EVENT_TRIGGER_VALUE:
        return

    # Выбираем один из сценариев.
    event_type = pseudo_random(seed + 1, EVENT_TYPE_COUNT)

    room_key = game_state.get("current_room")
    room = ROOMS.get(room_key, {})
    inventory = game_state.setdefault("player_inventory", [])

    if event_type == EVENT_TYPE_FIND:
        # Находка: монетка на полу.
        print("Вы замечаете на полу старую монетку.")
        items = room.setdefault("items", [])
        items.append("coin")
    elif event_type == EVENT_TYPE_SCARE:
        # Испуг.
        print("Вы слышите странный шорох неподалёку...")
        if any(item.lower().replace(" ", "_") == "sword" for item in inventory):
            print("Вы поднимаете меч, и существо отступает в темноту.")
    else:  # EVENT_TYPE_TRAP
        # Попытка срабатывания ловушки.
        if (
            room_key == "trap_room"
            and not any(
                item.lower().replace(" ", "_") == "torch" for item in inventory
            )
        ):
            print("Кажется, вы наступили на подозрительную плитку...")
            trigger_trap(game_state)

