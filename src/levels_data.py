"""The three handcrafted dungeon layouts.

Every level is a list of 14 strings with 20 characters each (one character =
one tile), so you can "see" the map right in the code and edit it easily.

Legend
------
#  stone wall                 T  wall with a torch
E  exit door (locked)         P  player start
K  key                        C  coin
H  treasure chest (bonus)     +  heart (restores 1 health)
^  floor spikes (always up)   v  floor spikes (go up and down)
B  barrel (obstacle)          X  crate (obstacle)
G  goblin (walks left/right)  S  skeleton (walks up/down)
L  slime (walks left/right, slowest)

The first two rows of the four left and four right columns are always walls,
because the HUD and the mini-map are drawn on top of them.
"""

LEVELS = [
    # ------------------------------------------------------------ level 1
    {
        "name": "The Cellar",
        "layout": [
            "#####" "##T#E" "#T###" "#####",
            "####." "....." "....." ".####",
            "#..C." "....." "....." ".C..#",
            "#..##" "##..#" "#..##" "##..#",
            "#..#." "....." "....." ".#..#",
            "#C.#." "##..^" "...##" ".#..#",
            "#..#." "#...C" "....B" ".#..#",
            "#..#." "#.###" "###.X" ".#.C#",
            "#..#." "#...^" "..K.#" ".#..#",
            "#..#." "H...." "....." ".#..#",
            "#..##" "##..#" "#..##" "##..#",
            "#...." "....." "....." "....#",
            "#.P.." ".B..." "...X." ".C..#",
            "#####" "#####" "#####" "#####",
        ],
    },
    # ------------------------------------------------------------ level 2
    {
        "name": "The Crypt",
        "layout": [
            "###########T#E#T####",
            "####............####",
            "#K...v....v.....C..#",
            "#################..#",
            "#....C......#......#",
            "#.....#...^....C...#",
            "#..#################",
            "#..C...#....G......#",
            "#....^....C..#.....#",
            "#################..#",
            "#..+..B.....v......#",
            "#...##....X.....C..#",
            "#.P....B.....^....H#",
            "####################",
        ],
    },
    # ------------------------------------------------------------ level 3
    {
        "name": "The Lost Vault",
        "layout": [
            "####T#E#T###########",
            "####....############",
            "#.....##############",
            "#...C.#............#",
            "#..####..........H.#",
            "#.....#....+#..X...#",
            "#.....#.G...#......#",
            "#L....#.....#..S...#",
            "#..^..#.^.^.#......#",
            "#.....#..v..#..X...#",
            "#...........#......#",
            "#v..........#.^..^.#",
            "#K....#.....#....P.#",
            "####################",
        ],
    },
]
