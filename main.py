from constants import *
from vector import Vector2
import tkinter as tk
import math
import random
from workers import Worker, Food, CreatureMethods, BaseCreature


def window_loop(win):
    Worker.update_workers()
    win.after(FRAME_DELAY, window_loop, win)


def setup_worker_groups():
    Worker.imply_groups("food", "collidable")


if __name__ == "__main__":
    root = tk.Tk()
    root.title(WINDOW_NAME)

    plain = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
    plain.pack()

    w = Worker(plain, 100, 100, speed=1, start_direction=1, groups_to_join="collidable")
    w.movement_energy, w.movement_constant = 0.1, 2
    w.movement_update = CreatureMethods.movement_using_v_with_speed
    print(w.size)
    o = Worker(plain, 150, 200, body_type="rectangle", size=[200, 10], groups_to_join="obsticles")

    plain.after(FRAME_DELAY, window_loop, root)
    root.mainloop()
