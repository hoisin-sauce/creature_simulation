# contains code for worker (sprites)
from collections.abc import Iterable
from constants import *
from vector import Vector2


class Worker:
    implied_groups = {"obsticles": {"collidable"}}
    groups = {"workers": set(),
              "collidable": set(),
              "obsticles": set(),
              "to be killed": set()}

    pressed_keys = set()
    
    @staticmethod
    def update_workers():
        for worker in Worker.groups["workers"]:
            if worker.is_dead:
                continue
            worker.game_update()

    @staticmethod
    def purge_dead_workers():
        for worker in Worker.groups["to be killed"]:
            worker.commit_to_kill()
        Worker.groups["to be killed"] = set()

    @staticmethod
    def add_to_groups(worker, groups):
        for group in groups:
            if group in Worker.groups.keys() and worker not in Worker.groups[group]:
                Worker.groups[group].add(worker)
                worker.groups.add(group)
                # print(f"{group} : {Worker.groups[group]}")
                if group in Worker.implied_groups.keys():
                    Worker.add_to_groups(worker, Worker.implied_groups[group])
            else:
                Worker.groups[group] = {worker}
                worker.groups.add(group)

    @staticmethod
    def imply_groups(original_group: str, implied_groups: Iterable):
        Worker.implied_groups[original_group] = implied_groups

    def __init__(self, canvas, x, y,
                 size=10,
                 color=DEFAULT_WORKER_COLOR,
                 speed=None,
                 start_direction=None,
                 is_bound_by_screen=True,
                 body_type="oval",
                 groups_to_join=None,
                 default_value=None):

        if start_direction is None:
            start_direction = Vector2()
        elif isinstance(start_direction, Iterable):
            start_direction = Vector2(*start_direction)
        elif isinstance(start_direction, (int, float)):
            start_direction = Vector2(start_direction)

        if size is None:
            size = Vector2()
        elif isinstance(size, Iterable):
            size = Vector2(*size)
        elif isinstance(size, (int, float)):
            size = Vector2(size)

        if speed is None:
            speed = Vector2()
        elif isinstance(speed, Iterable):
            speed = Vector2(*speed)

        if groups_to_join is None:
            groups_to_join = set()
        if isinstance(groups_to_join, str):
            groups_to_join = {groups_to_join}

        if default_value is None:
            default_value = size.magnitude

        if "workers" not in groups_to_join:
            groups_to_join.add("workers")

        self._size = size
        self._initial_size = size
        self.position = Vector2(x, y)
        self.direction = start_direction
        self.speed = speed
        self.canvas = canvas
        self.previous_pos = Vector2(x, y)
        self.is_bound_by_screen = is_bound_by_screen
        self._color = color
        self._body_type = body_type
        self.create_body()
        self.groups = set()
        self._value = default_value
        self.is_dead = False

        Worker.add_to_groups(self, groups_to_join)

    @property
    def initial_size(self):
        return self._initial_size

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        v = self.value
        self._value = value
        self.value_updated(v, value)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value: Vector2):
        self._size = value
        self.canvas.coords(self.body, self.position.x,
                           self.position.y,
                           self.position.x + self.size.x,
                           self.position.y + self.size.y)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self.canvas.itemconfig(self.body, fill=color)
        self._color = color

    @property
    def body_type(self):
        return self._body_type

    # noinspection PyAttributeOutsideInit
    def create_body(self):
        match self.body_type:
            case "oval":
                self.body = self.canvas.create_oval(self.position.x, self.position.y,
                                                    self.position.x + self.size.x, self.position.y + self.size.y,
                                                    fill=self.color)
            case "rectangle":
                self.body = self.canvas.create_rectangle(self.position.x, self.position.y,
                                                         self.position.x + self.size.x, self.position.y + self.size.y,
                                                         fill=self.color)
            case _:
                raise type

    def update_position(self):
        if self.position != self.previous_pos:
            delta_pos = self.position - self.previous_pos
            if not (delta_pos.x < 1 and delta_pos.y < 1):
                self.canvas.moveto(self.body, self.position.x, self.position.y)
            self.previous_pos = self.position

    def detect_collisions(self):
        collision_bodies = self.get_collision_bodies()
        for worker in Worker.groups["collidable"]:
            if worker is self:
                continue
            if worker.body in collision_bodies:
                self.handle_collision(worker)

    def handle_collision(self, other):
        if other in Worker.groups["obsticles"] and self in Worker.groups["collidable"]:
            self.position = self.previous_pos

    def get_collision_bodies(self):
        return self.canvas.find_overlapping(self.position.x,
                                            self.position.y,
                                            self.position.x + self.size.x,
                                            self.position.y + self.size.y)

    def update(self):
        pass

    def move(self, overall_movement: Vector2):
        if self.is_bound_by_screen:
            if self.motion_outside_bounds(overall_movement):
                return
        self.position += overall_movement

    def movement_update(self):
        current_movement = self.direction.normalised() * self.speed
        self.move(current_movement)

    def motion_outside_bounds(self, movement: Vector2):
        possible_position = self.position + movement
        return possible_position.x < 0 or \
            possible_position.y < 0 or \
            possible_position.x + self.size.x > WIDTH or \
            possible_position.y + self.size.y > HEIGHT

    def game_update(self):
        self.update()
        self.movement_update()
        self.detect_collisions()
        self.update_position()

    def kill(self):
        Worker.add_to_groups(self, ["to be killed"])
        self.is_dead = True

    def commit_to_kill(self):
        for group in self.groups:
            if group != "to be killed":
                Worker.groups[group].remove(self)
        self.canvas.delete(self.body)

    def value_updated(self, before, after):
        pass


class Food(Worker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Worker.add_to_groups(self, "food")

    def handle_collision(self, other: Worker):
        super().handle_collision(other)
        match other.groups:
            case "herbivore":
                self.kill()
                other.value += self.value


# noinspection PyUnresolvedReferences
class CreatureMethods:
    # requires movement constant

    def __init__(self):
        self.value = None

    def movement_proportional_to_v(self):
        current_movement = self.direction.normalised() * \
                           self.speed * \
                           min(self.value, self.movement_constant)
        if current_movement.x < 0.01:
            current_movement.x = 0
        if current_movement.y < 0.01:
            current_movement.y = 0
        self.move(current_movement)

    # requires movement energy constant
    def movement_uses_v(self):
        self.value -= max((self.position - self.previous_pos).magnitude * self.movement_energy, 0)
        if self.value < 0:
            self.value = 0

    def movement_using_v_with_speed(self):
        CreatureMethods.movement_proportional_to_v(self)
        CreatureMethods.movement_uses_v(self)

    # requires energy size constant
    def size_proportional_to_v(self, before, after):
        self.size *= after / before * self.energy_size_constant
        if after < 1:
            self.kill()

    def absorb(self, other):
        other.kill()
        self.value += other.value


class BaseCreature(Worker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Worker.add_to_groups(self, "creature")


class TestCreature(Worker):
    movement_update = CreatureMethods.movement_using_v_with_speed
    value_updated = CreatureMethods.size_proportional_to_v
