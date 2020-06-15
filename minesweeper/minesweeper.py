#!/usr/bin/env python3.8

import random

from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)


nums = {
    0: ":zero:",
    1: "||:one:||",
    2: "||:two:||",
    3: "||:three:||",
    4: "||:four:||",
    5: "||:five:||",
    6: "||:six:||",
    7: "||:seven:||",
    8: "||:eight:||",
    # 9: "||:nine:||",
}


class GuessingException(Exception):
    pass


class MineSweeper(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def msnew(self, ctx, width: int = 9, length: int = 9, bombs: int = 10):
        if bombs >= width * length:
            await ctx.send("Need to have less bombs than locations!")
            return

        board = Board(width, length, bombs)
        board.generate_board()
        output = str(board)
        if len(output) >= 2000:
            await ctx.send("Board too large!")
            return
        await ctx.send(output)


class Board(object):
    def __init__(self, width=10, length=10, bombs=15):
        self.width = width
        self.length = length
        self.bombs = bombs
        self.board = None
        self.mask = None

    def __str__(self):
        output = "\n".join(
            "".join(nums.get(cell, "||:boom:||") for cell in row) for row in self.board
        )
        return output

    def show_array(self, arr=None):
        if arr is None:
            arr = self.board
        return "\n".join(str(row) for row in arr)

    def solve_board(self):
        # zeros first
        for i, j in self.generate_positions():
            if self.board[j][i] == 0:
                self.mask[j][i] = 1
                for new_i, new_j in self.generate_valid_deltas(i, j):
                    self.mask[new_j][new_i] = 1
        print(self.show_array(self.mask))
        print('~')

        for _ in range(50):
            # while True:
            for i, j in self.generate_positions():
                if self.mask[j][i] == 0 or self.board[j][i] == 0 or self.mask[j][i] == 9:
                    continue

                nearby_bombs = list(self.find_near_bombs(i, j))
                if self.board[j][i] == len(nearby_bombs):
                    for new_i, new_j in self.find_open_spots(i, j):
                        self.mask[new_j][new_i] = 1

                # if all are bombs
                open_spots = list(self.find_open_spots(i, j))
                if self.board[j][i] == len(open_spots):
                    for new_i, new_j in open_spots:
                        self.mask[new_j][new_i] = 9

            break

        print(self.show_array(self.mask))

        for i, j in self.generate_positions():
            if self.mask[j][i] == 9:
                assert self.board[j][i] == 9

    def find_open_spots(self, i, j):
        for new_i, new_j in self.generate_valid_deltas(i, j):
            if self.mask[new_j][new_i] == 0:
                yield new_i, new_j

    def find_near_bombs(self, i, j):
        for new_i, new_j in self.generate_valid_deltas(i, j):
            if self.mask[new_j][new_i] == 9:
                yield new_i, new_j

    def generate_valid_deltas(self, i, j):
        for idelta in range(-1, 2):
            for jdelta in range(-1, 2):
                new_i = i + idelta
                new_j = j + jdelta

                if (
                    (idelta == 0 and jdelta == 0)
                    or new_i < 0
                    or new_j < 0
                    or new_i >= self.width
                    or new_j >= self.length
                ):
                    continue

                yield new_i, new_j

    def generate_positions(self):
        for i in range(self.width):
            for j in range(self.length):
                yield i, j

    def generate_board(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.length)]
        self.mask = [[0 for _ in range(self.width)] for _ in range(self.length)]

        for _ in range(self.bombs):
            while True:
                xloc = random.randint(0, self.width - 1)
                yloc = random.randint(0, self.length - 1)
                if self.board[yloc][xloc] == 0:
                    self.board[yloc][xloc] = 9
                    break

        for i in range(self.width):
            for j in range(self.length):
                if self.board[j][i] == 9:
                    continue

                num_bombs = 0
                for new_i, new_j in self.generate_valid_deltas(i, j):
                    if self.board[new_j][new_i] == 9:
                        num_bombs += 1

                self.board[j][i] = num_bombs

        return self.board


if __name__ == "__main__":
    board = Board()
    board.generate_board()
    print(str(board))
    print(board.show_array())
    print("~~~")
    print(board.solve_board())
