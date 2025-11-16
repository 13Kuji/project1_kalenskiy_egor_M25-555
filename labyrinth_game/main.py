#!/usr/bin/env python3
"""Entry point for the labyrinth game."""

from labyrinth_game.constants import COMMANDS
from labyrinth_game.player_actions import (
    get_input,
    move_player,
    show_inventory,
    take_item,
    use_item,
)
from labyrinth_game.utils import (
    attempt_open_treasure,
    describe_current_room,
    show_help,
    solve_puzzle,
)


def process_command(game_state: dict, command: str) -> None:
    """Parse and execute a player's command."""
    command = command.strip()
    if not command:
        print("Введите команду.")
        return

    parts = command.split(maxsplit=1)
    action = parts[0].lower()
    argument = parts[1].strip() if len(parts) > 1 else ""

    match action:
        case "look":
            describe_current_room(game_state)
        case "inventory" | "inv":
            show_inventory(game_state)
        case "help":
            show_help(COMMANDS)
        case "north" | "south" | "east" | "west":
            move_player(game_state, action)
        case "go" | "move":
            if not argument:
                print("Куда идти? Укажите направление (например, 'go north').")
            else:
                move_player(game_state, argument)
        case "take" | "get":
            if not argument:
                print("Что взять? Укажите предмет (например, 'take torch').")
            else:
                take_item(game_state, argument)
        case "use":
            if not argument:
                print("Что использовать? Укажите предмет (например, 'use torch').")
            else:
                use_item(game_state, argument)
        case "solve":
            # В комнате сокровищ пытаемся открыть сундук (ключом или кодом).
            if game_state.get("current_room") == "treasure_room":
                attempt_open_treasure(game_state)
            else:
                solve_puzzle(game_state)
        case "quit" | "exit":
            print("Выход из игры. Спасибо за игру!")
            game_state["game_over"] = True
        case _:
            print("Неизвестная команда.")


def main() -> None:
    """Main game loop."""
    game_state = {
        "player_inventory": [],
        "current_room": "entrance",
        "game_over": False,
        "steps_taken": 0,
    }

    print("Добро пожаловать в Лабиринт сокровищ!")
    describe_current_room(game_state)

    while not game_state["game_over"]:
        command = get_input("> ")
        process_command(game_state, command)


if __name__ == "__main__":
    main()

