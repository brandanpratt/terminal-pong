#!/usr/bin/env python3
"""Terminal Pong — a tiny curses Pong game. No dependencies, just Python 3.

Controls
  Left paddle : W / S
  Right paddle: Up / Down arrows (2-player mode)
  P           : pause      Q : quit
"""

import curses
import random
import time

WIN_SCORE = 7
FPS = 60
PADDLE_H = 5
PADDLE_SPEED = 30.0      # rows per second while a key is "held"
HOLD_TIME = 0.12         # how long one keypress keeps the paddle moving
BALL_START_SPEED = 30.0  # columns per second
BALL_SPEEDUP = 1.06
BALL_MAX_SPEED = 80.0
CPU_SPEED = {"easy": 12.0, "normal": 18.0, "hard": 26.0}


class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = float(y)
        self.dir = 0
        self.until = 0.0

    def press(self, direction, now):
        self.dir = direction
        self.until = now + HOLD_TIME

    def update(self, dt, now, top, bottom):
        if now > self.until:
            self.dir = 0
        self.y += self.dir * PADDLE_SPEED * dt
        self.clamp(top, bottom)

    def clamp(self, top, bottom):
        self.y = max(top, min(bottom - PADDLE_H, self.y))

    def rows(self):
        y = int(round(self.y))
        return range(y, y + PADDLE_H)


class Ball:
    def __init__(self):
        self.x = self.y = 0.0
        self.vx = self.vy = 0.0

    def serve(self, cx, cy, direction):
        self.x, self.y = float(cx), float(cy)
        self.vx = BALL_START_SPEED * direction
        self.vy = random.uniform(-0.5, 0.5) * BALL_START_SPEED * 0.6


def center(scr, y, text, attr=0):
    h, w = scr.getmaxyx()
    if 0 <= y < h:
        try:
            scr.addstr(y, max(0, (w - len(text)) // 2), text[: w - 1], attr)
        except curses.error:
            pass


def menu(scr):
    options = [
        ("1 Player  (vs CPU - easy)", ("cpu", "easy")),
        ("1 Player  (vs CPU - normal)", ("cpu", "normal")),
        ("1 Player  (vs CPU - hard)", ("cpu", "hard")),
        ("2 Players (same keyboard)", ("2p", None)),
        ("Quit", None),
    ]
    sel = 1
    scr.nodelay(False)
    while True:
        scr.erase()
        h, _ = scr.getmaxyx()
        top = max(1, h // 2 - 8)
        title = [
            "#####   ###  #   #  ####",
            "#   #  #   # ##  # #    ",
            "#####  #   # # # # #  ##",
            "#      #   # #  ## #   #",
            "#       ###  #   #  ####",
        ]
        for i, line in enumerate(title):
            center(scr, top + i, line, curses.A_BOLD | curses.color_pair(1))
        for i, (label, _) in enumerate(options):
            attr = curses.A_REVERSE if i == sel else 0
            center(scr, top + 7 + i, "  " + label + "  ", attr)
        center(scr, top + 14, "Up/Down + Enter to choose  |  W/S & Arrows move  |  P pause  |  Q quit",
               curses.A_DIM)
        center(scr, top + 15, "First to %d wins" % WIN_SCORE, curses.A_DIM)
        scr.refresh()
        k = scr.getch()
        if k in (curses.KEY_UP, ord("w"), ord("W")):
            sel = (sel - 1) % len(options)
        elif k in (curses.KEY_DOWN, ord("s"), ord("S")):
            sel = (sel + 1) % len(options)
        elif k in (10, 13, curses.KEY_ENTER, ord(" ")):
            return options[sel][1]
        elif k in (ord("q"), ord("Q"), 27):
            return None
        elif ord("1") <= k <= ord("5"):
            return options[k - ord("1")][1]


def play(scr, mode, level):
    scr.nodelay(True)
    h, w = scr.getmaxyx()
    if h < 15 or w < 40:
        scr.nodelay(False)
        scr.erase()
        center(scr, h // 2, "Terminal too small (need 40x15). Press any key.")
        scr.getch()
        return

    top, bottom = 2, h - 1          # playable rows: [top, bottom)
    left = Paddle(2, (top + bottom - PADDLE_H) // 2)
    right = Paddle(w - 3, (top + bottom - PADDLE_H) // 2)
    ball = Ball()
    score = [0, 0]
    ball.serve(w // 2, (top + bottom) // 2, random.choice((-1, 1)))
    paused = False
    wait_until = time.time() + 1.0   # short pause before each serve
    message = "Get ready!"
    last = time.time()
    winner = None

    while True:
        now = time.time()
        dt = min(now - last, 0.05)
        last = now

        # --- input -------------------------------------------------------
        while True:
            k = scr.getch()
            if k == -1:
                break
            if k in (ord("q"), ord("Q")):
                return
            if k in (ord("p"), ord("P")):
                paused = not paused
            elif k in (ord("w"), ord("W")):
                left.press(-1, now)
            elif k in (ord("s"), ord("S")):
                left.press(1, now)
            elif mode == "2p" and k == curses.KEY_UP:
                right.press(-1, now)
            elif mode == "2p" and k == curses.KEY_DOWN:
                right.press(1, now)
            elif mode == "cpu" and k == curses.KEY_UP:     # arrows work for P1 too vs CPU
                left.press(-1, now)
            elif mode == "cpu" and k == curses.KEY_DOWN:
                left.press(1, now)
            elif k == curses.KEY_RESIZE:
                return play(scr, mode, level)

        # --- update ------------------------------------------------------
        if not paused and winner is None:
            left.update(dt, now, top, bottom)
            if mode == "2p":
                right.update(dt, now, top, bottom)
            else:
                # CPU tracks the ball when it's coming its way, else drifts to centre
                target = ball.y if ball.vx > 0 else (top + bottom) / 2
                mid = right.y + PADDLE_H / 2
                step = CPU_SPEED[level] * dt
                if abs(target - mid) > 0.5:
                    right.y += step if target > mid else -step
                right.clamp(top, bottom)

            if now >= wait_until:
                message = ""
                ball.x += ball.vx * dt
                ball.y += ball.vy * dt

                # walls
                if ball.y < top:
                    ball.y = top + (top - ball.y)
                    ball.vy = abs(ball.vy)
                elif ball.y > bottom - 1:
                    ball.y = (bottom - 1) - (ball.y - (bottom - 1))
                    ball.vy = -abs(ball.vy)

                # paddles
                for pad, side in ((left, -1), (right, 1)):
                    hit_x = pad.x + 1 if side == -1 else pad.x - 1
                    crossing = ball.x <= hit_x if side == -1 else ball.x >= hit_x
                    moving_in = ball.vx < 0 if side == -1 else ball.vx > 0
                    if crossing and moving_in and int(round(ball.y)) in pad.rows():
                        ball.x = hit_x
                        speed = min(abs(ball.vx) * BALL_SPEEDUP, BALL_MAX_SPEED)
                        ball.vx = -side * speed
                        # where it hit the paddle decides the bounce angle
                        offset = (ball.y - (pad.y + PADDLE_H / 2)) / (PADDLE_H / 2)
                        ball.vy = offset * speed * 0.6 + pad.dir * 4

                # scoring
                scorer = None
                if ball.x < 0:
                    scorer = 1
                elif ball.x > w - 1:
                    scorer = 0
                if scorer is not None:
                    score[scorer] += 1
                    if score[scorer] >= WIN_SCORE:
                        winner = scorer
                    else:
                        ball.serve(w // 2, (top + bottom) // 2, 1 if scorer == 0 else -1)
                        wait_until = now + 0.8
                        message = "Point!"

        # --- draw --------------------------------------------------------
        scr.erase()
        p2name = "P2" if mode == "2p" else "CPU (%s)" % level
        center(scr, 0, "P1  %d   :   %d  %s" % (score[0], score[1], p2name), curses.A_BOLD)
        try:
            scr.hline(1, 0, curses.ACS_HLINE, w)
            scr.hline(bottom, 0, curses.ACS_HLINE, w)
            for y in range(top, bottom, 2):
                scr.addch(y, w // 2, ":", curses.A_DIM)
            for pad, cp in ((left, 2), (right, 3)):
                for y in pad.rows():
                    if top <= y < bottom:
                        scr.addch(y, pad.x, curses.ACS_CKBOARD, curses.color_pair(cp) | curses.A_BOLD)
            bx, by = int(round(ball.x)), int(round(ball.y))
            if winner is None and 0 <= bx < w and top <= by < bottom:
                scr.addch(by, bx, "O", curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass

        if paused:
            center(scr, h // 2, " PAUSED - press P ", curses.A_REVERSE)
        elif message:
            center(scr, h // 2 - 2, " %s " % message, curses.A_REVERSE)
        if winner is not None:
            name = "P1" if winner == 0 else p2name
            center(scr, h // 2 - 1, "  %s WINS!  %d - %d  " % (name, score[0], score[1]),
                   curses.A_REVERSE | curses.A_BOLD)
            center(scr, h // 2 + 1, "Press R to play again or Q for menu")
            scr.refresh()
            scr.nodelay(False)
            while True:
                k = scr.getch()
                if k in (ord("r"), ord("R")):
                    return play(scr, mode, level)
                if k in (ord("q"), ord("Q"), 27):
                    return
        scr.refresh()
        time.sleep(max(0, 1 / FPS - (time.time() - now)))


def main(scr):
    curses.curs_set(0)
    scr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_YELLOW, -1)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)
    while True:
        choice = menu(scr)
        if choice is None:
            return
        play(scr, *choice)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("Thanks for playing Terminal Pong!")
