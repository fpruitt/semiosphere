from models import Game, Player, BadMoveError, Mark, ACTION_COSTS

from random import randint


def main():
    print("\nSemiosphere \n")
    unordered_players = create_players_from_interactive_input()
    players = []

    # Determine player order randomly
    print("Randomly deciding the order of players...")
    while len(unordered_players) > 0:
        chosen_player = unordered_players.pop(randint(0, len(unordered_players) - 1))
        players.append(chosen_player)
        print(chosen_player.name)

    game = Game(grid_rows=11, grid_columns=8, players=players)
    for player in players:
        prompt_player_for_initial_placement(player=player, game=game)

    """
      Main game loop
    """
    dead_players = []
    while True:
        for player in players:
            player.planet_action_this_turn = False
            while player.moves_left > 0:
                prompt_player_for_turn(player=player, game=game)
        # Move Void Forward
        game.move_void_forward()

        # Handle players being taken by the void
        for player in players:
            if not player.alive:
                print("{} has been lost to the void.".format(player.name))
                dead_players.append(player)
                players.remove(player)

        # Check for win condition: All players dead except one
        if len(players) == 1:
            print("{} has won the game by abandoning his fellow players to be lost to the void.".format(
                    players[0].name)
            )
            exit()

        # Assign moves to players.
        # Moves earned by having marks in the void have already been awarded.
        for player in players:
            player.moves_left += ACTION_COSTS["initial_moves_per_turn"]

            if not player.has_planet():
                player.moves_left += ACTION_COSTS["planet_dropped_bonus"]


def create_players_from_interactive_input():
    players = []
    num_of_players = _get_player_count()
    for i in range(0, num_of_players):
        name = input("Enter player {player_number}'s name--> ".format(player_number=i + 1))
        players.append(Player(name))
    return players


def prompt_player_for_initial_placement(player, game, row=0):
    valid_entry = False
    while not valid_entry:
        column_start_str = input('{player_name}, which column would you like to start in? --> '.format(
            player_name=player.name
        ))
        try:
            starting_column = int(column_start_str)

            if not 0 <= starting_column < game.num_of_columns():
                raise ValueError
            try:
                game.move_player_to_cell(player=player, row_id=row, column_id=starting_column)
            except BadMoveError:
                raise ValueError
        except ValueError:
            print("Invalid entry, please enter a number between 0 and {} that is not already occupied.".format(game.num_of_columns() - 1))
        else:
            valid_entry = True

    print(game.grid.get_grid_as_ascii())


def prompt_player_for_turn(player, game):
    valid_entry = False
    print("{player_name}, it's your turn and you have {moves_left} action(s) remaining. What would you like to do?".format(
        player_name=player.name,
        moves_left=player.moves_left,
    ))
    if player.has_planet():
        print("You currently DO have your planet.")
    else:
        print("You currently DON'T have your planet.")
    print("\t1. Move Forward        Cost: {} Move(s)".format(ACTION_COSTS['move_forward']))
    print("\t2. Move Left           Cost: {} Move(s)".format(ACTION_COSTS['move_left']))
    print("\t3. Move Right          Cost: {} Move(s)".format(ACTION_COSTS['move_right']))
    print("\t4. Move Backwards      Cost: {} Move(s)".format(ACTION_COSTS['move_backwards']))
    print("\t5. Place a Mark        Cost: {} Move(s)".format(ACTION_COSTS['place_mark']))
    print("\t6. Erase a Mark        Cost: {} Move(s)".format(ACTION_COSTS['erase_mark']))
    print("\t7. Drop my Planet      Cost: {} Move(s)".format(ACTION_COSTS['drop_planet']))
    print("\t8. Enter Semiosphere   Cost: {} Move(s)".format(ACTION_COSTS['enter_semiosphere']))
    print("\t9. Leave Semiosphere   Cost: {} Move(s)".format(ACTION_COSTS['leave_semiosphere']))
    # print("9. Pick up my planet   Cost: {} Moves".format(ACTION_COSTS['pickup_planet']))

    while not valid_entry:
        choice_str = input("Enter a choice between 1 and 9: --> ")
        try:
            choice = int(choice_str)

            if not 1 <= choice <= 9:
                raise ValueError
        except ValueError:
            print("Invalid entry, please enter a number between 1 and 9 to mark your choice.")
        else:
            if 1 <= choice <= 4:
                row = player.current_cell.row
                column = player.current_cell.column

                if choice == 1:
                    row += 1
                    moves_to_lose = ACTION_COSTS["move_forward"]
                elif choice == 2:
                    column -= 1
                    moves_to_lose = ACTION_COSTS["move_left"]

                elif choice == 3:
                    column +=1
                    moves_to_lose = ACTION_COSTS["move_right"]

                else:
                    row -= 1
                    moves_to_lose = ACTION_COSTS["move_backwards"]

                if moves_to_lose > player.moves_left:
                    print("You don't have enough actions left to move that way.")
                elif row >= game.num_of_rows() or row < 0 or column >= game.num_of_columns() or column < 0:
                    print("You can't move that way!")
                else:
                    try:
                        game.move_player_to_cell(player=player, row_id=row, column_id=column)
                        player.moves_left -= moves_to_lose
                    except BadMoveError as e:
                        print(e)
                    else:
                        valid_entry = True
            elif choice == 5:
                row, column = _get_row_column_nums_from_player(game=game, action="place your mark")
                cell = game.grid.get_cell(row=row, column=column)

                # Can't place mark on an occupied cell, a cell with a planet already in it,
                # or a cell already containing a mark.
                if cell.has_mark():
                    print("You can't place a mark on a cell that already has a mark!")
                elif cell.has_planet():
                    print("You can't place a mark on top of an enemy planet!")
                elif cell.is_occupied():
                    print("You can't place a mark on top of an enemy player!")
                else:
                    mark = Mark(player=player, cell=cell)
                    print("Placed mark in cell at row {}, column {}".format(
                        mark.cell.row,
                        mark.cell.column
                    ))
                    player.moves_left -= ACTION_COSTS["place_mark"]
                    valid_entry = True

            elif choice == 6:
                if player.moves_left >= ACTION_COSTS["erase_mark"]:
                    row, column = _get_row_column_nums_from_player(game=game, action="erase a mark")
                    cell = game.grid.get_cell(row=row, column=column)
                    # You can't erase your own mark, or a non-existent mark.
                    if not cell.has_mark():
                        print("There isn't a mark to remove in that cell!")
                    elif cell.mark.player.id == player.id:
                        print("You can't erase your own mark!")
                    else:
                        cell.mark.erase_mark()
                        player.moves_left -= ACTION_COSTS["erase_mark"]
                        valid_entry = True
                else:
                    print("You don't have enough actions left to erase a mark! You need {moves_needed}".format(
                        moves_needed=ACTION_COSTS["erase_mark"]
                    ))

            elif choice == 7:
                if not player.has_planet():
                    print("You've already dropped your planet!")
                elif player.moves_left < ACTION_COSTS["drop_planet"]:
                    print("You don't have enough actions left to drop your planet!")
                else:
                    cell_behind_player = player.cell_behind(grid=game.grid)
                    if cell_behind_player:
                        if cell_behind_player.is_occupied():
                            print("You can't drop your planet on an occupied space!")
                        elif cell_behind_player.has_mark():
                            if not cell_behind_player.mark.player.id == player.id:
                                print("You can't drop your planet on a space with another player's mark!")
                        elif cell_behind_player.has_planet():
                            print("You can't drop your planet on top of another planet!")
                        else:
                            cell_behind_player.add_planet(planet=player.planet, player=player)
                            player.moves_left -= ACTION_COSTS["drop_planet"]
                            player.moves_left += ACTION_COSTS["planet_dropped_bonus"]
                            player.planet_action_this_turn = True
                            valid_entry = True
                    else:
                        print("You're on the back row! You can't drop your planet!")

            elif choice == 8:
                # Enter semiosphere. If with planet, game is won. If without planet, player enters semiosphere state
                if not player.current_cell.row == game.grid.get_number_of_rows() - 1:
                    print("You cannot enter the Semiosphere unless you are on the top row.")
                elif player.moves_left < ACTION_COSTS['enter_semiosphere']:
                    print("You need five actions to enter the Semiosphere.")
                else:
                    player.current_cell.remove_player()
                    player.in_semiosphere = True
                    if player.has_planet():
                        print("{name} has entered the semiosphere with his planet and won the game!".format(
                                name=player.name))
                        exit(0)
                    else:
                        print("{name} has entered the semiosphere, but they left "
                              "their planet behind to be swallowed up by the void.".format(name=player.name))
                        print("They must now stop other players from entering the semiosphere.")
                        player.moves_left -= ACTION_COSTS['enter_semiosphere']
                        valid_entry = True

            elif choice == 9:
                """
                Allow a player already in the semiosphere to exit. This is possibly useful for planet recovery.
                """
                if not player.in_semiosphere:
                    print("You can't leave the semiosphere if you aren't already in it!")
                elif game.grid.check_for_semiosphere_exit(player=player):
                    print("There is not a valid exit available for you at the moment.")
                else:
                    prompt_player_for_initial_placement(
                            player=player,
                            game=game,
                            row=game.grid.get_number_of_rows() - 1
                    )
                    player.moves_left -= ACTION_COSTS['leave_semiosphere']
                    valid_entry = True



            """
            elif choice == 9:
                if player.current_cell.has_planet() and player.current_cell.planet.player.id == player.id:
                    player.current_cell.remove_planet()
                    # Lose moves for picking your planet back up
                    if player.moves_left >= 2:
                        player.moves_left -= 2
                    else:
                        player.moves_left = 0
                    valid_entry = True
                else:
                    print("Your planet is not in this cell!")
            """

    print(game.grid.get_grid_as_ascii())


def _get_player_count():
    valid_entry = False
    num_of_players = 0
    while not valid_entry:
        num_of_players_str = input('How many people are playing? --> ')
        try:
            num_of_players = int(num_of_players_str)
            if num_of_players < 2 or num_of_players > 4:
                raise ValueError
        except ValueError:
            print("Invalid entry, please enter a number between 2 and 4.")
        else:
            valid_entry = True
    return num_of_players


def _get_row_column_nums_from_player(game, action):
    valid_row_str = False
    valid_column_str = False
    row_num = 0
    column_num = 0
    while not valid_row_str:
        try:
            row_num = int(input("In what row would you like to {action}? --> ".format(action=action)))
            if 0 >= row_num > game.num_of_rows():
                raise ValueError
        except ValueError:
            print("Invalid row number, please enter a value between 0 and {rows}".format(rows=game.num_of_rows() - 1))
        else:
            valid_row_str = True
    while not valid_column_str:
        try:
            column_num = int(input("In what column would you like to {action}? --> ".format(action=action)))
            if 0 >= column_num > game.num_of_columns():
                raise ValueError
        except ValueError:
            print(
                    "Invalid column number, please enter a value between 0 and {columns}".format(
                        columns=game.num_of_columns() - 1
                    )
            )
        else:
            valid_column_str = True
    return row_num, column_num


if __name__ == "__main__":
    main()
