import os
import tkinter as Tkinter
import time


def load_level(level_path):
    level = []
    with open(level_path) as f:
        for line in f:
            line = line.rstrip('\n')
            if len(line) == 0:
                continue
            level.append(line)
    return level


class Object:
    def __init__(self, uuid):
        self.uuid = uuid


class CellObject(Object):
    def __init__(self, uuid, x, y):
        super().__init__(uuid)
        self.x = x
        self.y = y


class Wall(CellObject):
    def __init__(self, uuid, x, y):
        super().__init__(uuid, x, y)


class Box(CellObject):
    def __init__(self, uuid, x, y):
        super().__init__(uuid, x, y)


class Door(CellObject):
    def __init__(self, uuid, x, y):
        super().__init__(uuid, x, y)


class Player(CellObject):
    def __init__(self, uuid, x, y, color):
        super().__init__(uuid, x, y)
        self.origin = None
        self.chosen = False
        self.color = color


class Origin(CellObject):
    def __init__(self, uuid, x, y, color):
        super().__init__(uuid, x, y)
        self.player = None
        self.chosen = False
        self.color = color


class Selection(CellObject):
    def __init__(self, uuid, x, y):
        super().__init__(uuid, x, y)


class Cell:
    def __init__(self):
        self.objects = {}

    def add_object(self, obj):
        self.objects[obj.uuid] = obj

    def del_object(self, obj):
        del self.objects[obj.uuid]

    def get_box(self):
        for obj in self.objects.values():
            if isinstance(obj, Box):
                return obj
        return None

    def get_door(self):
        for obj in self.objects.values():
            if isinstance(obj, Door):
                return obj
        return None

    def get_player(self):
        for obj in self.objects.values():
            if isinstance(obj, Player):
                return obj
        return None

    def get_origins(self):
        origins = []
        for obj in self.objects.values():
            if isinstance(obj, Origin):
                origins.append(obj)
        return sorted(origins, key=lambda origin: origin.color)

    def is_player_passable(self):
        for obj in self.objects.values():
            for cls in [Wall, Box, Player]:
                if isinstance(obj, cls):
                    return False
        return True

    def is_box_passable(self):
        for obj in self.objects.values():
            for cls in [Wall, Box, Player, Door]:
                if isinstance(obj, cls):
                    return False
        return True


class Game:
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    down = 0
    right = 1
    up = 2
    left = 3

    def __init__(self, level, gui):
        self.__uuid_counter = 0
        self.gui = gui
        self.n = len(level)
        self.m = len(level[0])
        self.gui.set_grid(self.n, self.m)
        self.grid = [[Cell() for i in range(self.m)] for j in range(self.n)]
        self.objects = {}
        self.player_queue = []
        self.origin_queue = []
        self.chosen_player = None
        self.chosen_origin = None
        self.is_choose_mode = False
        self.is_select_mode = False
        self.is_win = False
        self.selection = None
        player_point = None
        door_point = None
        for i in range(self.n):
            for j in range(self.m):
                if level[i][j] == '#':
                    self.make_wall(i, j)
                elif level[i][j] == 'X':
                    self.make_box(i, j)
                elif level[i][j] == '*':
                    assert player_point is None
                    player_point = (i, j)
                elif level[i][j] == '@':
                    assert door_point is None
                    door_point = (i, j)
                elif level[i][j] == '.':
                    pass
                else:
                    assert False
        self.make_player(*player_point)
        door = self.make_door(*door_point)
        self.make_origin(self.chosen_player, door)

    def update_chosen_player(self):
        if self.chosen_player is not None:
            self.chosen_player.chosen = False
            self.gui.move_object(self.chosen_player)
        if len(self.player_queue) == 0:
            self.chosen_player = None
        else:
            self.chosen_player = self.player_queue[0]
            self.chosen_player.chosen = True
            self.gui.move_object(self.chosen_player)

    def update_chosen_origin(self):
        if self.chosen_origin is not None:
            self.chosen_origin.chosen = False
            self.gui.move_object(self.chosen_origin)
        if len(self.origin_queue) == 0:
            self.chosen_origin = None
        else:
            self.chosen_origin = self.origin_queue[0]
            self.chosen_origin.chosen = True
            self.gui.move_object(self.chosen_origin)

    def out_of_grid(self, x, y):
        return x < 0 or x >= self.n or y < 0 or y >= self.m

    def is_player_passable(self, x, y):
        return not self.out_of_grid(x, y) and self.grid[x][y].is_player_passable()

    def is_box_passable(self, x, y):
        return not self.out_of_grid(x, y) and self.grid[x][y].is_box_passable()

    def move_player(self, player, d):
        x0 = player.x
        y0 = player.y
        x1 = x0 + self.dx[d]
        y1 = y0 + self.dy[d]
        x2 = x1 + self.dx[d]
        y2 = y1 + self.dy[d]
        if self.is_player_passable(x1, y1):
            self.move_cell_object(player, x1, y1)
        if not self.out_of_grid(x1, y1):
            box = self.grid[x1][y1].get_box()
            if box is not None and self.is_box_passable(x2, y2):
                self.move_cell_object(box, x2, y2)
                self.move_cell_object(player, x1, y1)

    def move_selection(self, d):
        x0 = self.selection.x
        y0 = self.selection.y
        x1 = x0 + self.dx[d]
        y1 = y0 + self.dy[d]
        if not self.out_of_grid(x1, y1):
            self.move_cell_object(self.selection, x1, y1)

    def appear_player(self):
        if len(self.player_queue) >= 4:
            return
        x = self.selection.x
        y = self.selection.y
        if self.is_player_passable(x, y):
            player = self.make_player(x, y)
            self.make_origin(player)
            self.exit_select_mode()

    def choose_origin(self, origin):
        player = self.chosen_player
        if len(self.player_queue) == 1:
            self.gui.win()
            self.is_win = True
            return
        if origin.color == player.color:
            return
        new_player = origin.player
        new_origin = player.origin
        new_origin.color = new_player.color
        new_player.origin = new_origin
        new_origin.player = new_player
        self.player_queue = self.player_queue[1:]
        self.update_chosen_player()
        self.exit_choose_mode()
        self.del_cell_object(player)
        self.del_cell_object(origin)
        self.gui.move_object(new_origin)

    def send_dir(self, d):
        if self.is_select_mode:
            self.move_selection(d)
        elif self.is_choose_mode:
            if d in [self.right, self.down]:
                self.origin_queue = self.origin_queue[1:] + self.origin_queue[:1]
            else:
                self.origin_queue = self.origin_queue[-1:] + self.origin_queue[:-1]
            self.update_chosen_origin()
        elif self.is_win:
            return
        else:
            self.move_player(self.chosen_player, d)

    def send_action(self):
        if self.is_select_mode:
            self.appear_player()
        elif self.is_choose_mode:
            self.choose_origin(self.chosen_origin)
        elif self.is_win:
            return
        else:
            origins = self.grid[self.chosen_player.x][self.chosen_player.y].get_origins()
            if len(origins) == 0:
                return
            elif len(origins) == 1:
                self.choose_origin(origins[0])
            else:
                self.origin_queue = origins
                self.update_chosen_origin()
                self.is_choose_mode = True

    def send_cancel(self):
        if self.is_select_mode:
            self.exit_select_mode()
        elif self.is_choose_mode:
            self.exit_choose_mode()
        elif self.is_win:
            return
        else:
            self.player_queue = self.player_queue[1:] + self.player_queue[:1]
            self.update_chosen_player()

    def send_menu(self):
        if self.is_select_mode:
            return
        elif self.is_choose_mode:
            return
        elif self.is_win:
            return
        else:
            self.make_selection(self.chosen_player.x, self.chosen_player.y)

    def move_cell_object(self, obj, x, y):
        self.grid[obj.x][obj.y].del_object(obj)
        obj.x = x
        obj.y = y
        self.grid[obj.x][obj.y].add_object(obj)
        self.gui.move_object(obj)

    def del_cell_object(self, obj):
        self.grid[obj.x][obj.y].del_object(obj)
        del self.objects[obj.uuid]
        self.gui.del_object(obj)

    def send_new(self):
        self.gui.reset()

    def new_uuid(self):
        uuid = self.__uuid_counter
        self.__uuid_counter += 1
        return uuid

    def add_cell_object(self, obj):
        self.objects[obj.uuid] = obj
        self.grid[obj.x][obj.y].add_object(obj)
        self.gui.add_object(obj)
        return obj

    def make_wall(self, x, y):
        wall = Wall(self.new_uuid(), x, y)
        return self.add_cell_object(wall)

    def make_box(self, x, y):
        box = Box(self.new_uuid(), x, y)
        return self.add_cell_object(box)

    def make_door(self, x, y):
        door = Door(self.new_uuid(), x, y)
        return self.add_cell_object(door)

    def make_player(self, x, y):
        colors = set(player.color for player in self.player_queue)
        color = 0
        while color in colors:
            color += 1
        player = Player(self.new_uuid(), x, y, color)
        self.add_cell_object(player)
        self.player_queue.insert(0, player)
        self.update_chosen_player()
        return player

    def make_origin(self, player, door=None):
        if door is None:
            door = player
        origin = Origin(self.new_uuid(), door.x, door.y, player.color)
        player.origin = origin
        origin.player = player
        return self.add_cell_object(origin)

    def make_selection(self, x, y):
        selection = Selection(self.new_uuid(), x, y)
        self.selection = selection
        self.is_select_mode = True
        return self.add_cell_object(selection)

    def exit_select_mode(self):
        self.del_cell_object(self.selection)
        self.selection = None
        self.is_select_mode = False

    def exit_choose_mode(self):
        self.origin_queue = []
        self.update_chosen_origin()
        self.is_choose_mode = False


class Window(Tkinter.Tk):
    scale = 3
    cell_size = 20 * scale
    cell_selection_width = 2 * scale
    player_pad = 2 * scale
    player_selection_width = 2 * scale
    origin_size = 6 * scale
    origin_pad = 1 * scale
    origin_selection_width = 1 * scale
    font_size = 15 * scale
    player_colors = ['yellow', 'sky blue', 'plum1', 'tan1']

    def __init__(self, level_path, *args, **kwargs):
        self.level_path = level_path
        Tkinter.Tk.__init__(self, *args, **kwargs)

        self.canvas = None
        self.shapes = {}
        self.game = Game(load_level(self.level_path), self)

        self.bind('<Any-KeyPress>', self.control)

    def reset(self):
        self.shapes = {}
        self.canvas.pack_forget()
        self.game = Game(load_level(self.level_path), self)

    def win(self):
        self.canvas.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2,
            text="You Win", font=("Purisa", self.font_size), fill='purple'
        )

    def set_grid(self, n, m):
        self.canvas = Tkinter.Canvas(self, width=m * self.cell_size, height=n * self.cell_size)
        self.canvas.pack()

    def control(self, event=None):
        key = event.keysym
        print(key)
        if key == 'Left':
            self.game.send_dir(Game.left)
        if key == 'Right':
            self.game.send_dir(Game.right)
        if key == 'Up':
            self.game.send_dir(Game.up)
        if key == 'Down':
            self.game.send_dir(Game.down)
        if key == 'z':
            self.game.send_action()
        if key == 'x':
            self.game.send_cancel()
        if key == 'c':
            self.game.send_menu()
        if key == 'n':
            self.game.send_new()

        else:
            pass
        return

    def add_wall(self, wall):
        return [
            self.canvas.create_rectangle(
                wall.y * self.cell_size,
                wall.x * self.cell_size,
                (wall.y + 1) * self.cell_size,
                (wall.x + 1) * self.cell_size,
                fill='gray40',
                tags='wall'
            )
        ]

    def add_box(self, box):
        return [
            self.canvas.create_rectangle(
                box.y * self.cell_size,
                box.x * self.cell_size,
                (box.y + 1) * self.cell_size,
                (box.x + 1) * self.cell_size,
                fill='tan4',
                tags='box'
            )
        ]

    def add_door(self, door):
        return [
            self.canvas.create_rectangle(
                door.y * self.cell_size,
                door.x * self.cell_size,
                (door.y + 1) * self.cell_size,
                (door.x + 1) * self.cell_size,
                fill='pale green',
                tags='door'
            )
        ]

    def add_player(self, player):
        return [
            self.canvas.create_oval(
                player.y * self.cell_size + self.player_pad,
                player.x * self.cell_size + self.player_pad,
                (player.y + 1) * self.cell_size - self.player_pad,
                (player.x + 1) * self.cell_size - self.player_pad,
                width=self.player_selection_width if player.chosen else 1,
                fill=self.player_colors[player.color],
                tags='player'
            )
        ]

    def add_origin(self, origin):
        x0 = origin.x * self.cell_size
        y0 = origin.y * self.cell_size
        x0 += (origin.color // 2 % 2) * (self.cell_size - self.origin_size)
        y0 += (origin.color % 2) * (self.cell_size - self.origin_size)
        return [
            self.canvas.create_oval(
                y0 + self.origin_pad,
                x0 + self.origin_pad,
                y0 + self.origin_size - self.origin_pad,
                x0 + self.origin_size - self.origin_pad,
                width=self.cell_selection_width if origin.chosen else 1,
                fill=self.player_colors[origin.color],
                tags='origin'
            )
        ]

    def add_selection(self, selection):
        return [
            self.canvas.create_rectangle(
                selection.y * self.cell_size,
                selection.x * self.cell_size,
                (selection.y + 1) * self.cell_size,
                (selection.x + 1) * self.cell_size,
                outline='orange',
                width=self.cell_selection_width,
                tags='selection'
            )
        ]

    def add_object(self, obj):
        if isinstance(obj, Wall):
            self.shapes[obj.uuid] = self.add_wall(obj)
        elif isinstance(obj, Box):
            self.shapes[obj.uuid] = self.add_box(obj)
        elif isinstance(obj, Door):
            self.shapes[obj.uuid] = self.add_door(obj)
        elif isinstance(obj, Player):
            self.shapes[obj.uuid] = self.add_player(obj)
        elif isinstance(obj, Origin):
            self.shapes[obj.uuid] = self.add_origin(obj)
        elif isinstance(obj, Selection):
            self.shapes[obj.uuid] = self.add_selection(obj)
        else:
            assert False

    def del_object(self, obj):
        for shape in self.shapes[obj.uuid]:
            self.canvas.delete(shape)
        del self.shapes[obj.uuid]

    def move_object(self, obj):
        self.del_object(obj)
        self.add_object(obj)


def main():
    level = input("Enter level number: ")
    level = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'levels', level + '.txt')
    window = Window(level, className=" Time Traveler ")
    while True:
        window.update()
        window.update_idletasks()
        time.sleep(0.09)


if __name__ == '__main__':
    main()
