#!/usr/bin/env python3.8

import random
from pprint import pprint as pp

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
    async def msnew(self, ctx, width: int = 14, length: int = 14, bombs: int = 40):
        if bombs >= width * length:
            await ctx.send("Need to have less bombs than locations!")
            return

        num_boards = 1
        cboard = Board(width, length, bombs)
        while True:
            if cboard.solve_board():
                break

            if num_boards > 1000:
                await ctx.send('Unable to find a solvable board!')
                return

            cboard = Board()
            num_boards += 1

        output = str(cboard)
        if len(output) >= 2000:
            await ctx.send("Board too large!")
            return

        await ctx.send(output)


class Board(object):
    def __init__(self, width=14, length=14, bombs=40):
        self.width = width
        self.length = length
        self.bombs = bombs
        self.board = None
        self.mask = None

        self.generate_board()

    def __str__(self):
        output = [[0 for _ in range(self.width)] for _ in range(self.length)]
        for i, j in self.generate_positions():
            output[j][i] = nums.get(self.board[j][i], "||:boom:||")
            if self.board[j][i] != 0 and any(
                self.board[nj][ni] == 0 for ni, nj in self.generate_valid_deltas(i, j)
            ):
                output[j][i] = output[j][i][2:-2]
        output = "\n".join("".join(cell for cell in row) for row in output)
        return output

    def generate_solvable(self):
        for _ in range(10):
            self.generate_board()
            self.solve_board()
            if all(all(c != -1 for c in row) for row in self.mask):
                break

    def show_array(self, arr=None):
        if arr is None:
            arr = self.board
        return "\n".join(
            "".join(str({9: "x", -1: " "}.get(x, x)).center(3) for x in row)
            for row in arr
        )

    def solve_board(self):
        solvable = False
        # initial reveal
        for i, j in self.generate_positions():
            if self.board[j][i] == 0:
                self.mask[j][i] = 0
                for ni, nj in self.generate_valid_deltas(i, j):
                    self.mask[j][i] = self.board[j][i]

        last = None
        for i in range(50):
            last = [c for row in self.mask for c in row]
            # print(self.show_array(self.mask))
            # print("---")
            for i, j in self.generate_positions():
                # skip already-found bombs
                if self.mask[j][i] == 9:
                    continue

                # if we've discovered all bombs here, reveal around
                spots_to_reveal = []
                if self.mask[j][i] == 0:
                    for ni, nj in self.generate_valid_deltas(i, j):
                        if self.mask[nj][ni] == -1:
                            spots_to_reveal.append((ni, nj))

                while True:
                    if len(spots_to_reveal) == 0:
                        break
                    ni, nj = spots_to_reveal.pop(0)
                    num_bombs = len(
                        [
                            (bi, bj)
                            for bi, bj in self.generate_valid_deltas(ni, nj)
                            if self.mask[bj][bi] == 9
                        ]
                    )
                    value = self.board[nj][ni] - num_bombs
                    self.mask[nj][ni] = value
                    if value == 0:
                        for nni, nnj in self.generate_valid_deltas(ni, nj):
                            if self.mask[nnj][nni] == -1:
                                spots_to_reveal.append((nni, nnj))

                # now if we haven't learned anything or if we have already learned everything, skip
                if self.mask[j][i] in [-1, 0]:
                    continue

                # for our new point,
                # count how many untested spots are nearby
                untested = []
                for ni, nj in self.generate_valid_deltas(i, j):
                    if self.mask[nj][ni] == -1:
                        untested.append((ni, nj))

                # and if the numbers line up then all those untested spots MUST be bombs
                if len(untested) == self.mask[j][i]:
                    # since we've found all bombs, decrement to zero
                    self.mask[j][i] = 0
                    for ni, nj in untested:
                        self.mask[nj][ni] = 9  # mark bombs

                        # now for each bomb, look at all identified points around and decrement by one
                        for bi, bj in self.generate_valid_deltas(ni, nj):
                            if self.mask[bj][bi] not in [9, -1, 0]:
                                self.mask[bj][bi] -= 1

            # if we found all the bombs then we done!
            if len([c for row in self.mask for c in row if c == 9]) == self.bombs:
                # convert all remaining unfound points to zeros
                # self.mask = [[c if c != -1 else 0 for c in row] for row in self.mask]
                solvable = True
                break

            if last == [c for row in self.mask for c in row]:
                solvable = False
                break

        # print(self.show_array(self.mask))

        for i, j in self.generate_positions():
            if self.mask[j][i] == 9:
                assert self.board[j][i] == 9

        return solvable

    def generate_valid_deltas(self, i, j):
        for idelta in range(-1, 2):
            for jdelta in range(-1, 2):
                ni = i + idelta
                nj = j + jdelta

                if (
                    (idelta == 0 and jdelta == 0)
                    or ni < 0
                    or nj < 0
                    or ni >= self.width
                    or nj >= self.length
                ):
                    continue

                yield ni, nj

    def generate_positions(self):
        for i in range(self.width):
            for j in range(self.length):
                yield i, j

    def generate_board(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.length)]
        self.mask = [[-1 for _ in range(self.width)] for _ in range(self.length)]

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
                for ni, nj in self.generate_valid_deltas(i, j):
                    if self.board[nj][ni] == 9:
                        num_bombs += 1

                self.board[j][i] = num_bombs

        return self.board


if __name__ == "__main__":
    num_boards = 1
    cboard = Board()
    while True:
        if cboard.solve_board():
            break

        cboard = Board()
        num_boards += 1

    print(num_boards)
    print(cboard.show_array())
    print(cboard.show_array(cboard.mask))
