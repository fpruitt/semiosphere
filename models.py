import uuid


ACTION_COSTS = {
    "move_forward": 1,
    "move_backwards": 0,
    "move_left": 1,
    "move_right": 1,
    "place_mark": 1,
    "erase_mark": 2,
    "drop_planet": 1,
    "pickup_planet_resulting_cost": 2,
    "enter_semiosphere": 5,
    "mark_voided": 1,
    "leave_semiosphere": 0,
    "initial_moves_per_turn": 3,
    "planet_dropped_bonus": 2,
}


class Cell:
    """
    Stateful representation of a single cell on the game board.
    """
    STATES = {
        "empty": " ",
        "occupied": "O",
        "voided": "X",
    }
    MODIFIERS = {
        "marked": "/",
        "contains_planet": "P"
    }

    state = "empty"
    modifiers = []
    occupied_by = None
    planet = None
    mark = None

    def __init__(self, row, column):
        self.row = row
        self.column = column

    def __str__(self):
        return "Cell in row {}, column {} with state {} and modifiers {}".format(
            self.row,
            self.column,
            self.state,
            print(', '.join(self.modifiers))
        )

    def mark_for_void(self):
        self.state = "voided"

    def is_empty(self):
        return self.state == "empty"

    def is_occupied(self):
        return self.state == "occupied"

    def is_voided(self):
        return self.state == "voided"

    def has_mark(self):
        return self.mark is not None

    def has_planet(self):
        return self.planet is not None

    def add_planet(self, planet, player):
        self.modifiers.append("contains_planet")
        self.planet = planet
        self.planet.drop_planet(cell=self)

    def remove_planet(self):
        self.planet.pick_up_planet()
        self.planet = None
        self.modifiers.remove("contains_planet")

    def add_mark(self, mark, player):
        if self.has_mark():
            raise BadMarkError(cell=self, player=player)
        print("Adding mark to cell {}".format(self))
        self.modifiers.append("marked")
        self.mark = mark

    def remove_mark(self):
        self.modifiers.remove("marked")
        self.mark = None

    def valid_for_player_to_enter(self, player):
        valid_to_enter = True
        # Players cannot move on top of already-occupied cells
        if self.is_occupied():
            valid_to_enter = False

        # Players cannot move on top of cells with planets in them unless the planet is their own.
        elif self.has_planet() and self.planet.player.id != player.id:
            valid_to_enter = False

        # Players cannot move into cells with their own planet if they've already performed a planet action this turn.
        elif self.has_planet() and self.planet.player.id == player.id and player.planet_action_this_turn:
            valid_to_enter = False

        # Players cannot move on top of cells with marks on them unless the mark is their own.
        elif self.has_mark() and self.mark.player.id != player.id:
            valid_to_enter = False

        # Players cannot move into the void
        elif self.is_voided():
            valid_to_enter = False

        return valid_to_enter

    def set_player(self, player):
        if self.valid_for_player_to_enter(player=player):
            self.occupied_by = player
            self.state = "occupied"
            player.current_cell = self
            if self.has_planet():
                assert(self.planet.player.id == player.id)
                self.remove_planet()
                if player.moves_left >= 2:
                    player.moves_left -= 2
                else:
                    player.moves_left = 0
                print("{name} picked up their planet, losing {actions_required} actions. ".format(
                    name=player.name,
                    actions_required=ACTION_COSTS['pickup_planet_resulting_cost']
                ))
            return True
        else:
            return False

    def remove_player(self):
        if self.occupied_by is not None:
            self.occupied_by = None
            self.state = "empty"
        else:
            print("No player to remove from this cell!")

    def get_cell_as_ascii(self):
        """
        Get the contents of the cell in short form.
        Used when printing a grid.
        :return: A variable-lengthed string containing single-character state + modifier representations.
        """
        return "{state}{modifiers}".format(
                state=self.STATES[self.state],
                modifiers=self.printable_modifiers()
        )

    def printable_modifiers(self):
        """
        Get text representation of the modifiers attached to this cell.
        :return: A variable-lengthed string containing the single-character modifiers attached to this cell.
        """
        mods = ""
        if self.has_mark():
            mods += "/"
        if self.has_planet():
            mods += "p"
        return mods


class Planet:
    LOCATIONS = [
        "player",
        "cell"
    ]

    def __init__(self, player):
        self.player = player
        self.location = "player"
        self.current_cell = None
        self.is_voided = False

    def drop_planet(self, cell):
        self.current_cell = cell
        self.location = "cell"

    def pick_up_planet(self):
        self.location = "player"

        self.current_cell = None

    def is_dropped(self):
        return self.location == "cell"


class Mark:
    def __init__(self, player, cell):
        self.player = player
        self.cell = cell
        self.cell.add_mark(mark=self, player=player)

    def erase_mark(self):
        self.cell.remove_mark()
        del self


class Grid:
    """
    Stateful representation of the NxN grid of cells that make up the game.
    Cells arranged in form [rows][columns]
    """

    def __init__(self, game, num_of_rows, num_of_columns):
        self.id = uuid.uuid4()
        self.game = game
        self.cells = []
        for row_id in range(0, num_of_rows):
            row = list()
            for column_id in range(0, num_of_columns):
                row.append(Cell(row_id, column_id))
            self.cells.append(row)

    def __str__(self):
        return "{rows}x{columns} Grid object from game {game_id} with unique id {id}".format(
            rows=self.get_number_of_rows(),
            columns=self.get_number_of_columns(),
            game_id=self.game.id,
            id=self.id,
        )

    def get_number_of_rows(self):
        return len(self.cells)

    def get_number_of_columns(self):
        return len(self.cells[0])

    def get_cell(self, row, column):
        return self.cells[row][column]

    def check_for_semiosphere_exit(self, player):
        """
        Check to see if there is a valid exit from the semiosphere available.
        :return: True if there is a cell that the player can move to from the semiosphere, false if there is not.
        """
        for cell in self.cells[self.get_number_of_rows() - 1]:
            if cell.valid_for_player_to_enter(player=player):
                return True
        return False

    def mark_row_for_void(self, row_id_to_mark):
        """
        Mark an entire row in this grid as taken by the void.
        :param row_id_to_mark: The id of the row to mark as void.
        """
        for cell in self.cells[row_id_to_mark]:
            if cell.is_occupied():
                cell.occupied_by.alive = False
            if cell.has_mark():
                cell.mark.player.moves_left += 1
                print("The void has awarded {} with {} point for leaving a mark for the void to take.".format(
                    cell.mark.player.name,
                    ACTION_COSTS['mark_voided']
                ))
            if cell.has_planet():
                cell.planet.is_voided = True
                print("{}'s planet has been lost to the void.".format(cell.planet.player.name))
            cell.mark_for_void()

    def get_grid_as_ascii(self):
        """
        Create an ascii representation of the current grid state.
        Assumes there are less than 100 columns & less than 4 states per cell for proper formatting.
        :return:
        """
        grid_str = ""
        # Add semiosphere header at the top
        grid_str += self._add_header(grid_str)

        # Add rows, iterating through the list backwards.
        for row_id, row in reversed(list(enumerate(self.cells))):
            grid_str += self._get_row_as_ascii(row_id, row)

        # Print extra row at the bottom with column labels
        final_row = "   |"
        for column_id, _ in enumerate(self.cells[0]):
            # Prepend 0 if needed
            if column_id < 10:
                final_row += " 0{} |".format(column_id)
            else:
                final_row += " {} |".format(column_id)
        final_row += "\n"
        grid_str += final_row
        return grid_str

    def _add_header(self, grid_str):
        # Add semiosphere at top
        # 3 + 4 * NUM_ROWS + NUM_ROWS - 1 - LEN(“SEMIOSPHERE: ”)
        grid_str += "   |"
        num_columns = len(self.cells[0])
        num_internal_chars = (num_columns * 4) + (num_columns - 1)
        for i in range(0, num_internal_chars):
            grid_str += "="
        grid_str += "|\n   |SEMIOSPHERE "
        # Add player icons for the number of players in the semiosphere
        num_in_semiosphere = len(self.game.players_in_semiosphere())
        for player in self.game.players_in_semiosphere():
            grid_str += "O "
        for i in range(0, num_internal_chars - 12 - (2 * num_in_semiosphere)):
            grid_str += " "
        grid_str += "|\n   |"
        for i in range(0, num_internal_chars):
            grid_str += "="
        grid_str += "|\n   |"
        for i in range(0, num_internal_chars):
            grid_str += "_"
        grid_str += "|\n"
        return grid_str

    @staticmethod
    def _get_row_as_ascii(row_id, row):
        """
        Helper function for printing an ascii representation of the grid.
        :param row_id: int representing the id of the row
        :param row: list containing Cell elements
        :return: a string representation of a row in the grid.
        """
        # Add row label, with appropriate padding if needed
        if row_id < 10:
            row_str = "{}  |".format(row_id)
        else:
            row_str = "{} |".format(row_id)

        # Print each cell. To keep the grid aligned, each cell must contain only four characters and a vertical bar.
        for column_id, cell in enumerate(row):
            cell_str = cell.get_cell_as_ascii()
            assert(0 <= len(cell_str) <= 4)
            if len(cell_str) == 0:
                cell_str = "    |"
            elif len(cell_str) == 1 or len(cell_str) == 3:
                cell_str = " {}  |".format(cell_str)
            elif len(cell_str) == 2:
                cell_str = " {} |".format(cell_str)
            elif len(cell_str) == 4:
                cell_str = "{}|".format(cell_str)
            row_str += cell_str
        row_str += "\n"
        return row_str


class Player:

    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name
        self.planet = Planet(player=self)
        self.points = 0
        self.moves_left = 3
        self.current_cell = None
        self.alive = True
        self.planet_action_this_turn = False
        self.in_semiosphere = False

    def has_planet(self):
        return not self.planet.is_dropped()

    def cell_to_left(self, grid):
        """
        Returns the Cell object that is to the left of this player, or None if the player is on the far left.
        :param grid: The game grid
        :return: The Cell object to the left of the player, or None
        """
        column = self.current_cell.column_number - 1
        if column >= 0:
            return grid.cells[self.current_cell.row][column]
        else:
            return None

    def cell_to_right(self, grid):
        """
        Returns the Cell object that is to the right of this player, or None if the player is on the far right.
        :param grid: The game grid
        :return: The Cell object to the right of the player, or None
        """
        column = self.current_cell.column_number + 1
        if column <= grid.get_number_of_columns():
            return grid.cells[self.current_cell.row][column]
        else:
            return None

    def cell_above(self, grid):
        """
        Returns the Cell object that is above this player, or None if the player is at the top of the grid.
        :param grid: The game grid
        :return: The Cell object above the player, or None
        """
        row = self.current_cell.row_number + 1
        if row <= grid.get_number_of_rows() - 1:
            return grid.cells[row][self.current_cell.column]
        else:
            return None

    def cell_behind(self, grid):
        """
        Returns the Cell object that is behind this player, or None if the player is at the bottom of the grid.
        :param grid: The game grid
        :return: The Cell object below the player, or None
        """
        row = self.current_cell.row - 1
        if row >= 0:
            return grid.cells[row][self.current_cell.column]
        else:
            return None


class Game:

    def __init__(self, grid_rows, grid_columns, players):
        self.id = uuid.uuid4()
        self.grid = Grid(game=self, num_of_rows=grid_rows, num_of_columns=grid_columns)
        self.current_void_row = 0
        # self.players = [Player(name="Frost"), Player(name="lolwut?")]
        self.players = players
        print(self.grid.get_grid_as_ascii())

    def move_void_forward(self):
        print("Row #{} has been lost to the void...\n".format(self.current_void_row))
        self.grid.mark_row_for_void(self.current_void_row)
        self.current_void_row += 1
        print(self.grid.get_grid_as_ascii())

    def num_of_rows(self):
        return self.grid.get_number_of_rows()

    def num_of_columns(self):
        return self.grid.get_number_of_columns()

    def move_player_to_cell(self, player, row_id, column_id):
        cell = self.grid.cells[row_id][column_id]
        old_cell = player.current_cell
        if not cell.set_player(player):
            raise BadMoveError(player=player, cell=cell)
        else:
            if old_cell is None:
                # This is the first placement.
                player.current_cell = cell
            else:
                old_cell.remove_player()

    def players_in_semiosphere(self):
        players = []
        for player in self.players:
            if player.in_semiosphere:
                players.append(player)
        return players


class CellError(Exception):
    def __init__(self, player, cell):
        self.player = player
        self.cell = cell

class BadMoveError(CellError):
    def __str__(self):
        return "Player {name} cannot enter the cell found at row {row_number} column {column_number}".format(
            name=self.player.name,
            row_number=self.cell.row,
            column_number=self.cell.column,
        )

class BadMarkError(CellError):
    def __str__(self):
        return "Player {name} cannot place a mark on cell at position {row_number} column {column_number}".format(
            name=self.player.name,
            row_number=self.cell.row,
            column_number=self.cell.column,
        )
