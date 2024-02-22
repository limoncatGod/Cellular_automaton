import pygame as p
import random
import numpy as np
import threading
from pygame.locals import *
from sys import exit
import time


start_time = time.thread_time()
# Константы цветов RGB
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 170, 0)
RED = (255, 0, 0)
cell_size = 10
ROOLS = [[[2,3],[3]], [[2,3,4],[3]],[[2],[2,3,4]]]
system=[[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
option = 0
root = None
is_game_started = False
mutex = threading.Lock()


def starting_rules():
    global option, ROOLS
    print("Options: \n0 - Standart Life\n1- Maze Creator\n2- Chaos\n3 - Own rule")
    try:
        option = int(input("Enter mode:"))
        if option not in [0, 1, 2, 3]:
            print("Excepted number of ROOL: 0, 1 or 2")
            starting_rules()
        elif option == 3:
            try:
                birth = list(map(int, input("Enter birth number cells separated by space:").split()))
                alive = list(map(int, input("Enter alive number cells separated by space:").split()))
                ROOLS.append([birth, alive])
                set_display()
            except ValueError:
                print("Excepted integer number!")
                starting_rules()
        else:
            set_display()
    except ValueError:
        print("Excepted integer number!")
        starting_rules()

def set_display():
    global root
    print("Set the size of display in format width height:\n 100 100")
    try:
        display = list(map(int, input("Enter size:").split()))
        root = p.display.set_mode((display[0], display[1]))
        set_size_of_cells()
    except ValueError:
        print("Enter two integer numbers separated be space")
        set_display()
    except IndexError:
        print("Write exactly TWO numbers")
        set_display()

def set_size_of_cells():
    global cell_size
    try:
        cell_size = int(input("Enter size of cell:"))
        print("Draw with your mouse (left button - draw, right - erase) and press S to start, for restart press R")
    except ValueError:
        print("Enter one integer number")
        set_size_of_cells()


args = []
number_of_process = 1


def set_args():
    global args, number_of_process
    print("Options: \n1 - 1 process\n2 - 2 process\n4 - 4 process")
    arguments_4 = [[0, width//2, 0, height//2], [width//2, width, height//2, height], [width//2, width, 0 , height//2], [0, width//2, height//2, height]]
    arguments_2 = [[0, width//2, 0, height], [width//2, width, 0, height]]
    arguments_1 = [[0, width, 0, height]]
    arguments_16 = [[0, width // 4, 0, height // 4], [width // 4, width // 2, 0, height // 4], [width // 2, 3 * width // 4, 0, height // 4], [3 * width // 4, width, 0, height // 4],
                    [0, width // 4, height // 4, height // 2], [width // 4, width // 2, height // 4, height // 2], [width // 2, 3 * width // 4, height // 4, height // 2], [3 * width // 4, width, height // 4, height // 2],
                    [0, width // 4, height // 2, 3 * height // 4], [width // 4, width // 2, height // 2, 3 * height // 4], [width // 2, 3 * width // 4, height // 2, 3 * height // 4], [3 * width // 4, width, height // 2, 3 * height // 4],
                    [0, width // 4, 3 * height // 4, height], [width // 4, width // 2, 3 * height // 4, height], [width // 2, 3 * width // 4, 3 * height // 4, height], [3 * width // 4, width, 3 * height // 4, height]
                    ]
    option = int(input("Enter mode:"))
    if option == 1:
        number_of_process = 1
        args = arguments_1
    elif option == 2:
        number_of_process = 2
        args = arguments_2
    elif option == 4:
        number_of_process = 4
        args = arguments_4


starting_rules()
width = root.get_width() // cell_size
height = root.get_height() // cell_size
cells = [[random.choice([0,1]) for j in range(width)] for i in range(height)]
#cells = [[0 for j in range(height)] for i in range(width)]
#cells[width//2] = [1 for j in range(height)]
cells_next = [[0 for j in range(height)] for i in range(width)]
set_args()

# Функция определения кол-ва соседей
def near(pos: list , system=[[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]):
    count = 0
    for i in system:
        if cells[(pos[0] + i[0]) % width][(pos[1] + i[1]) % height] == 1:
            count += 1
    return count


def draw_field(w_x, w_x2, h_y, h_y2):
    global root, cells, cells_next, ROOLS
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            p.draw.rect(root, RED if cells[i][j] == 1 else BLACK, [i * cell_size, j * cell_size, cell_size, cell_size])
    for i in range(w_x, w_x2):
        for j in range(h_y, h_y2):
            if cells[i][j]:
                if near([i, j]) not in ROOLS[option][0]:
                    cells_next[i][j] = 0
                else:
                    cells_next[i][j] = 1
            elif near([i, j]) in ROOLS[option][1]:
                cells_next[i][j] = 1
            else:
                cells_next[i][j] = 0


def run_threads(count, args):
    global cells, cells_next
    cells_next = [[0 for j in range(height)] for i in range(width)]
    threads = [
        threading.Thread(target=draw_field, args=(args[i][0], args[i][1], args[i][2], args[i][3],))
        for i in range(0, count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    cells = cells_next


FPS = p.time.Clock()
p.event.set_allowed([p.QUIT, p.KEYDOWN, p.K_s, p.K_r])
while 1:
    #FPS.tick(60)
    for i in p.event.get():
        if i.type == QUIT:
            exit()
        if i.type == p.KEYDOWN:
            if i.key == p.K_s:
                is_game_started = True
                start_time = time.thread_time()
            if i.key == p.K_r:
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"Время выполнения программы: {execution_time} секунд")
                is_game_started = False
                cells = [[0 for j in range(height)] for i in range(width)]
    '''for i in range(0, width):
        for j in range(0, height):
            #print(cells[i][j],i,j)
            p.draw.rect(root, RED if cells[i][j] == 1 else BLACK, [i * cell_size, j * cell_size, cell_size, cell_size])'''
    #отрисовка сетки
    #for i in range(0, root.get_height()):
        #p.draw.line(root, WHITE, (0, i * cell_size), (root.get_width(), i * cell_size))
    #for j in range(0, root.get_width()):
        #p.draw.line(root, WHITE, (j * cell_size, 0), (j * cell_size, root.get_height()))
    # Обновляем экран
    p.display.update()
    if is_game_started:
        run_threads(number_of_process, args)
    else:
        pressed = p.mouse.get_pressed()
        pos = p.mouse.get_pos()
        if pressed[0] and 0 <= pos[0] // cell_size < width and 0 <= pos[1] // cell_size < height:
            cells[pos[0]//cell_size][pos[1]//cell_size] = 1
        if pressed[2] and 0 <= pos[0] // cell_size < width and 0 <= pos[1] // cell_size < height:
            cells[pos[0]//cell_size][pos[1]//cell_size] = 0
        for i in range(0, width):
            for j in range(0, height):
                p.draw.rect(root, RED if cells[i][j] == 1 else BLACK,
                            [i * cell_size, j * cell_size, cell_size, cell_size])
