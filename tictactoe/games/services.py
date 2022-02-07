from typing import Union
from tictactoe.games.models import Game, Move, MARKS
from tictactoe.users.models import User
import random


class GameService:
    """Service class that manages the flow of the game.

    Service class' methods are ignorant of caller origin and can be used freely
    regardless of the request-handling framework.
    """

    user_model = User

    @classmethod
    def set_up_player(cls, game: Game, user: user_model) -> None:
        """Sets up a creator of a game as a random player in the newly created game.

        Args:
            game (Game): Game object instance for which action ought to be performed
            user (user_model): user who should be assigned as one of the players
        """
        is_player_1 = random.choice((True, False))

        if is_player_1:
            game.player_1 = user
        else:
            game.player_2 = user

        game.save()

    @classmethod
    def join_game(cls, game: Game, user: user_model) -> dict:
        """Assigns given user to the game.

        Args:
            game (Game): Game object instance for which action ought to be performed
            user (user_model): user who joins the game

        Returns:
            dict: dict providing information about action competion or errors that occured
        """
        if game.status == "finished":
            return {"error": "This game has already finished"}

        if game.is_user_in_game(user=user):
            return {"error": "You already joined this game"}

        if game.is_full:
            return {"error": "This game is already full"}

        if game.player_1 is None:
            game.player_1 = user
        else:
            game.player_2 = user

        game.status = "in_progress"
        game.save()

        return {"status": "Joined a game"}

    @classmethod
    def move(cls, game: Game, data: dict, user: user_model) -> dict:
        """Performs the user requested move in a game.

        Args:
            game (Game): Game object instance for which action ought to be performed
            data (dict): coordinates (row, column) for the move
            user (user_model): user who performs the move

        Returns:
            dict: dict providing information about action competion or errors that occured
        """
        if not game.is_user_in_game(user=user):
            return {"error": "You are not part of this game"}

        if game.status == "finished":
            return {"error": "This game has already finished"}

        if game.status == "not_started":
            return {"error": "Wait for the other player to join"}

        player, mark = game.get_next_player_and_mark()
        if player != user:
            return {"error": "This is not your turn now"}

        if not game.is_move_valid(row=data["row"], column=data["column"]):
            return {"error": "You cannot make this move"}

        move = Move.objects.create(
            game=game,
            player=user,
            row=data["row"],
            column=data["column"],
            mark=mark,
        )

        cls._update_game_status(game=game)

        return {"move": move}

    @classmethod
    def _update_game_status(cls, game: Game) -> None:
        """Updates the status of a game after checking if there are any winners or if game has concluded without one.

        Args:
            game (Game): Game object instance for which action ought to be performed
        """
        winning_mark = Grid(game).find_winner()

        if winning_mark is None:
            winner = None
        elif winning_mark == "draw":
            winner = "draw"
        else:
            winner = (
                game.player_1 if winning_mark == MARKS["player_1"] else game.player_2
            )

        if winner is None:
            game.next_turn = (
                game.player_1 if game.next_turn != game.player_1 else game.player_2
            )
        elif winner == "draw":
            game.status = "finished"
            game.next_turn = None
        else:
            game.winner = winner
            game.status = "finished"
            game.next_turn = None
        game.save()


class Grid:
    """Supporting class that allows to find a winner of a game (if any)."""

    def __init__(self, game: Game, grid_len: int = 3) -> None:
        self.grid_len = grid_len
        self.moves = game.moves
        self.grid = [[None] * self.grid_len for _ in range(self.grid_len)]
        self.rng = range(self.grid_len)

    def find_winner(self) -> Union[str, None]:
        """Returns winning mark or None.

        Returns:
            Union[str, None]: winning mark (char) or None
        """
        self._prepare_grid()

        draw = "draw" if self._is_draw else None

        return self._is_row_win or self._is_col_win or self._is_diag_win or draw

    def _prepare_grid(self) -> None:
        """Populates grid with all of the moves performed for given game."""
        for row in self.rng:
            for col in self.rng:
                try:
                    self.grid[row][col] = self.moves.get(row=row, column=col).mark
                except Move.DoesNotExist:
                    pass

    @property
    def _is_draw(self) -> bool:
        """The boolean property for a draw case.

        Returns:
            bool: True if there are no more moves available
        """
        return not any(any(mark is None for mark in row) for row in self.grid)

    @property
    def _is_row_win(self) -> Union[str, None]:
        """The boolean property for a row win case.

        Returns:
            Union[str, None]: winning mark or None
        """
        for row in self.grid:
            row_marks = [x for x in row if x is not None]
            if len(set(row_marks)) == 1:
                if len(row_marks) == self.grid_len:
                    return row[0]

        return None

    @property
    def _is_col_win(self) -> Union[str, None]:
        """The boolean property for a col win case.

        Returns:
            Union[str, None]: winning mark or None
        """
        for c in self.rng:
            column_marks = [
                self.grid[r][c] for r in self.rng if self.grid[r][c] is not None
            ]
            if len(set(column_marks)) == 1:
                if len(column_marks) == self.grid_len:
                    return column_marks[0]

        return None

    @property
    def _is_diag_win(self) -> Union[str, None]:
        """The boolean property for a diagonal win case.

        Returns:
            Union[str, None]: winning mark or None
        """
        p_diag_marks = [
            self.grid[i][i] for i in self.rng if self.grid[i][i] is not None
        ]
        n_diag_marks = [
            self.grid[self.grid_len - i - 1][i]
            for i in self.rng
            if self.grid[self.grid_len - i - 1][i] is not None
        ]

        if len(set(p_diag_marks)) == 1:
            if len(p_diag_marks) == self.grid_len:
                return list(p_diag_marks)[0]
        if len(set(n_diag_marks)) == 1:
            if len(n_diag_marks) == self.grid_len:
                return list(n_diag_marks)[0]

        return None
