#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque

'''
Набір функції для обробки карти, фігури, отримання точок можливого ходу
'''
def parse_map() -> list[list[str]]:
    height = int(input().strip().split()[1]) + 1
    game_map = []
    for _ in range(height):
        line = input().strip()
        if not line or len(line.split()) < 2:
            continue
        game_map.append(list(line.split()[1]))
    return game_map

def parse_figure() -> list[tuple[int, int]]:
    line = input().strip()
    if not line.startswith("Piece"):
        raise ValueError(f"Unexpected input: {line}")

    height = int(line.split()[1])
    figure = []
    for i in range(height):
        line = input().strip()
        for ind, elem in enumerate(line):
            if elem != '.':
                figure.append((height - i - 1, ind))
    return figure


def check_position(map: list[list[str]], figure: list[tuple[int, int]],
                   position: tuple[int, int], player: str) -> bool:
    same_counter = 0
    height, width = len(map), len(map[0])
    x_, y_ = position

    for coords in figure:
        x, y = x_ + coords[1], y_ + coords[0]

        if not (0 <= x < width and 0 <= y < height):
            return False

        if map[y][x].upper() not in ('.', player):
            return False

        if map[y][x].upper() == player:
            same_counter += 1

    return same_counter == 1


def get_all_positions(map: list[list[str]], figure:
                    list[tuple[int, int]], player: str) -> list[tuple[int, int]]:
    possible_pos = []
    for y, elem_y in enumerate(map):
        for x, elem_x in enumerate(elem_y):
            if check_position(map, figure, (x, y), player):
                possible_pos.append((x, y))

    return possible_pos

'''
Набір функцій для розрахунків подальшого ходу
'''


def compute_free_cells(map: list[list[str]]) -> int:
    return sum(row.count('.') for row in map)


def compute_enemy_density(map: list[list[str]], enemy: str) -> int:
    return sum(row.count(enemy.upper()) + row.count(enemy.lower()) for row in map)


def compute_player_density(map: list[list[str]], player: str) -> int:
    return sum(row.count(player.upper()) + row.count(player.lower()) for row in map)


def compute_distance_to_center(map: list[list[str]], player: str) -> float:
    """
    Рахує середнє значення до центру карти
    """
    height, width = len(map), len(map[0])
    center_x, center_y = width // 2, height // 2
    total_distance = 0
    count = 0

    for y, row in enumerate(map):
        for x, cell in enumerate(row):
            if cell.upper() == player:
                total_distance += ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                count += 1

    return total_distance / count if count > 0 else float('inf')


def determine_strategy_with_thresholds(map, player, enemy):

    free_cells = compute_free_cells(map)
    enemy_density = compute_enemy_density(map, enemy)
    player_density = compute_player_density(map, player)
    distance_to_center_player = compute_distance_to_center(map, player)
    distance_to_center_enemy = compute_distance_to_center(map, enemy)

    if free_cells > 50 and player_density > enemy_density:
        return "expansion"

    if enemy_density > player_density + 10:
        return "blocking"

    if distance_to_center_player > distance_to_center_enemy:
        return "centralization"

    return "expansion"

"""
Отримання оптимальної координати
"""

#функція розширення
def compute_density(map: list[list[str]], figure: list[tuple[int, int]], position: tuple[int, int]) -> int:
    x_, y_ = position
    height, width = len(map), len(map[0])
    empty_cells = 0

    for fy, fx in figure:
        x, y = x_ + fx, y_ + fy
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= ny < height and 0 <= nx < width and map[ny][nx] == '.':
                empty_cells += 1

    return empty_cells


def compute_free_area(map: list[list[str]], figure: list[tuple[int, int]], position: tuple[int, int]) -> int:
    visited = set()
    x_, y_ = position
    height, width = len(map), len(map[0])

    def dfs(x, y):
        if (x, y) in visited or not (0 <= y < height and 0 <= x < width) or map[y][x] != '.':
            return 0
        visited.add((x, y))
        return 1 + sum(dfs(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)])

    free_area = 0
    for fy, fx in figure:
        x, y = x_ + fx, y_ + fy
        free_area += dfs(x, y)

    return free_area


def compute_distance_to_edge(map: list[list[str]], position: tuple[int, int]) -> float:
    x, y = position
    height, width = len(map), len(map[0])
    return min(x, y, width - x - 1, height - y - 1)


def expansion_score(map: list[list[str]], figure: list[tuple[int, int]],
                    position: tuple[int, int]) -> float:
    w_density = 0.5
    w_free_area = 0.3
    w_distance_to_edge = 0.2

    density = compute_density(map, figure, position)
    free_area = compute_free_area(map, figure, position)
    distance_to_edge = compute_distance_to_edge(map, position)

    return w_density * density + w_free_area * free_area - w_distance_to_edge * distance_to_edge


#функція централізації
def compute_free_area_near_center(map: list[list[str]]) -> int:
    center_x, center_y = len(map[0]) // 2, len(map) // 2
    visited = set()
    free_area = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    queue = deque([(center_x, center_y)])
    while queue:
        x, y = queue.popleft()

        if (x, y) in visited or not (0 <= y < len(map) and 0 <= x < len(map[0])):
            continue
        visited.add((x, y))

        if map[y][x] == '.':
            free_area += 1
            for dx, dy in directions:
                queue.append((x + dx, y + dy))

    return free_area


def compute_distance_to_center_for_pos(map: list[list[str]], position: tuple[int, int]) -> float:
    x, y = position
    height, width = len(map), len(map[0])
    center_x, center_y = width // 2, height // 2

    return ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5


def centralization_score(map: list[list[str]], position: tuple[int, int]) -> float:
    w_distance_to_center = 0.6
    w_center_free_area = 0.4

    distance_to_center = compute_distance_to_center_for_pos(map, position)
    center_free_area = compute_free_area_near_center(map)

    return -w_distance_to_center * distance_to_center + w_center_free_area * center_free_area


#функція блокування

def compute_enemy_density1(map: list[list[str]], figure: list[tuple[int, int]],
                           position: tuple[int, int]) -> int:
    x_, y_ = position
    height, width = len(map), len(map[0])
    enemy_cells = 0

    for fy, fx in figure:
        x, y = x_ + fx, y_ + fy
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= ny < height and 0 <= nx < width and map[ny][nx] in ("x", "X"):
                enemy_cells += 1

    return enemy_cells

def compute_distance_to_enemy(map: list[list[str]], figure: list[tuple[int, int]],
                            position: tuple[int, int]) -> float:

    x_, y_ = position
    enemy_positions = [
        (x, y) for y, row in enumerate(map) for x, cell in enumerate(row) if cell in ("x", "X")
    ]

    if not enemy_positions:
        return float('inf')

    total_distance = 0
    count = 0

    for fy, fx in figure:
        fx, fy = x_ + fx, y_ + fy
        for ex, ey in enemy_positions:
            total_distance += ((fx - ex) ** 2 + (fy - ey) ** 2) ** 0.5
            count += 1

    return total_distance / count if count > 0 else float('inf')
def blocking_score(map: list[list[str]], figure: list[tuple[int, int]], position: tuple[int, int]) -> float:
    w_enemy_density = 0.7
    w_distance_to_enemy = 0.3

    enemy_density = compute_enemy_density1(map, figure, position)
    distance_to_enemy = compute_distance_to_enemy(map, figure, position)

    return w_enemy_density * enemy_density - w_distance_to_enemy * distance_to_enemy



def find_best_position(map: list[list[str]], figure: list[tuple[int, int]],
                       player: str, strategy: str) -> tuple[int, int]:

    possible_positions = get_all_positions(map, figure, player)
    best_position = None
    best_score = float('-inf')
    score = 0

    for position in possible_positions:
        if strategy == "expansion":
            score = expansion_score(map, figure, position)
        elif strategy == "blocking":
            score = blocking_score(map, figure, position)
        elif strategy == "centralization":
            score = centralization_score(map,position)

        if score > best_score:
            best_score = score
            best_position = position

    return best_position


def main():
    import sys
    player_line = input().strip()
    player = 'O' if "p1" in player_line else 'X'
    enemy = 'X' if player == 'O' else 'O'

    while True:
        try:
            game_map = parse_map()
            figure = parse_figure()

            strategy = determine_strategy_with_thresholds(game_map, player, enemy)

            best_position = find_best_position(game_map, figure, player, strategy)

            if best_position:
                print(best_position[1], best_position[0])
            else:
                print("0 0")
                break
        except EOFError:
            print("Game over", file=sys.stderr)
            break

if __name__ == '__main__':
    main()