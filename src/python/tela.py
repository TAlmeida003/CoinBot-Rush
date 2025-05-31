import os
import asyncio
import keyboard
import math

TAMANHO_PISTA: int = 150 - 2
SIZE_BUFFER: int = 200

LEFT_OFFESET: int = 0
RIGHT_OFFESET: int = 50
DOWN_OFFESET: int = 100
UP_OFFESET: int = 150

ANGLE: int = 30
SPEED: int = 1


def decoder(color: str) -> str:
    if color == 'v':  #vermelho
        return "\033[91m" + "1" + "\033[0m"  # instrução
    elif color == 'b':  #amarelo
        return "\033[93m" + "2" + "\033[0m"
    elif color == "g": # verde
        return "\033[92m" + "3" + "\033[0m"
    elif color == "y":  # azul
        return "\033[94m" + "4" + "\033[0m"
    else:  #cinza
        return "0"


def mov_screen(x: int, y: int, angulo: int, go: str ) -> tuple[int, int, int, int]:
    new_x, new_y = x, y

    if go == "f":
        new_x += SPEED * math.cos(math.radians(angulo))
        new_y -= SPEED * math.sin(math.radians(angulo))
    elif go == "r":
        new_x -= SPEED * math.cos(math.radians(angulo))
        new_y += SPEED * math.sin(math.radians(angulo))

    new_x_v = calculate_value(int(new_x))
    new_y_v = calculate_value(int(new_y))
    
    return new_x, new_y, new_x_v, new_y_v

def calculate_value(coord):
    if coord <= 71:
        return -coord
    elif coord <= 96:
        return 3 * coord - 276
    else:
        return -coord + 128

def select_color(coord: int, index: int, buffer: list[str], offset: int) -> None:
    if coord % 4 == 0 or coord % 4 == 2:
        if (index % 4 == 0 and coord % 4 == 0) or (index % 4 != 0 and coord % 4 != 0):
            buffer[index + offset] = 'b'
            buffer[index + 1 + offset] = 'b'
        else:
            buffer[index + offset] = 'v'
            buffer[index + 1 + offset] = 'v'
    else:
        if (index % 4 == 0 and coord % 4 == 1) or (index % 4 != 0 and coord % 4 != 1):
            buffer[index + offset] = 'b'
            buffer[index + 1 + offset] = 'v'
        else:
            buffer[index + offset] = 'v'
            buffer[index + 1 + offset] = 'b'


def fill_empty_space(index: int, buffer: list[str], offset: int) -> None:
    buffer[index + offset] = 'c'


def draw_track(x, y, buffer) -> None:
    for i in range(50):

        faixa_y = (i > (-y + 67)) and (i < (-y + TAMANHO_PISTA + 2))
        faixa_x = (i > (-x + 67)) and (i < (-x + TAMANHO_PISTA + 2))

        if i % 2 == 0 and i < 50:
            select_color(y, i, buffer, LEFT_OFFESET)
            select_color(x, i, buffer, UP_OFFESET)
            select_color(y, i, buffer, RIGHT_OFFESET)
            select_color(x, i, buffer, DOWN_OFFESET)

        # parede esquerda
        if not ((i > 19 - y and x <= 22 and i < 198 - y) or (faixa_y and x >= TAMANHO_PISTA - 50)):
            fill_empty_space(i, buffer, LEFT_OFFESET)

        # parede direita
        if not ((i > 19 - y and x >= TAMANHO_PISTA - 2 and i < 198 - y) or (faixa_y and x <= 70)):
            fill_empty_space(i, buffer, RIGHT_OFFESET)

        # parede superior
        if not ((i > 19 - x and y <= 22 and i < 198 - x) or (faixa_x and y >= TAMANHO_PISTA - 50)):
            fill_empty_space(i, buffer, UP_OFFESET)

        # parede inferior
        if not ((i > 19 - x and y >= TAMANHO_PISTA - 2 and i < 198 - x) or (faixa_x and y <= 70)):
            fill_empty_space(i, buffer, DOWN_OFFESET)

    #set_borda(buffer)


def select_borda(a, b, buffer):
    if buffer[a] != 'c':
        buffer[b] = buffer[a]
        buffer[b + 1] = buffer[a + 1]
    elif buffer[b] != 'c':
        buffer[a] = buffer[b]
        buffer[a + 1] = buffer[b + 1]


def set_borda(buffer: list[str]) -> None:
    select_borda(0 + LEFT_OFFESET, 0 + UP_OFFESET, buffer)
    select_borda(0 + RIGHT_OFFESET, 48 + UP_OFFESET, buffer)
    select_borda(48 + LEFT_OFFESET, 0 + DOWN_OFFESET, buffer)
    select_borda(48 + RIGHT_OFFESET, 48 + DOWN_OFFESET, buffer)

#limitar o apagar
def simularTela(buffer, array, offset_x, offset_y, prev_x_v, prev_y_v, x_bool, y_bool, screen_x, screen_y) -> None:

    for i in range(2):
        for j in range(50):
            if screen_x < 23 or screen_x > 97:
                if 50 > (i + offset_x + 20) >= 0:
                    array[j][i + offset_x + 20] = decoder(buffer[j + LEFT_OFFESET])

                if (50 > (i + prev_x_v + 20) >= 0) and (abs(prev_x_v - offset_x) > 1):
                    if x_bool:
                        if (screen_x > 97 and buffer[j + LEFT_OFFESET] != 'c'):
                            array[j][i + prev_x_v + 20] = decoder("g") #y
                        elif screen_x < 23:
                            array[j][i + prev_x_v + 20] = decoder("c")
                    else:
                        if (screen_x < 23 or screen_x > 97):#and buffer[j + LEFT_OFFESET] != 'c':
                            array[j][i + prev_x_v + 20] = decoder("c")

            if screen_y > 145 or screen_y < 71:
                if 50 > (i + offset_y + 48 + 20) >= 0:
                    array[i + 48 + offset_y + 20][j] = decoder(buffer[j + DOWN_OFFESET])

                if (50 > (i + prev_y_v + 48 + 20) >= 0) and (abs(prev_y_v - offset_y) > 1):
                    if y_bool:
                        if (screen_y > 145 or screen_y < 71):# and buffer[j + DOWN_OFFESET] != 'c':
                            array[i + 48 + prev_y_v + 20][j] = decoder("c")
                    else:
                        if (screen_y < 71 and buffer[j + DOWN_OFFESET] != 'c'):
                            array[i + 48 + prev_y_v + 20][j] = decoder("g")
                        elif screen_y > 145:
                            array[i + 48 + prev_y_v + 20][j] = decoder("c")

            if screen_y < 23 or screen_y > 97:
                if 50 > (i + offset_y + 20) >= 0:
                    array[i + offset_y + 20][j] = decoder(buffer[j + UP_OFFESET])

                if (50 > (i + prev_y_v + 20) >= 0) and (abs(prev_y_v - offset_y) > 1):
                    if y_bool:
                        if (screen_y > 97 and buffer[j + UP_OFFESET] != 'c'):
                            array[i + prev_y_v + 20][j] = decoder("g")
                        elif screen_y < 23:
                            array[i + prev_y_v + 20][j] = decoder("c")
                    else:
                        if (screen_y < 23 or screen_y > 97):# and buffer[j + UP_OFFESET] != 'c':
                            array[i + prev_y_v + 20][j] = decoder("c")

            if screen_x > 145 or screen_x < 71:
                if 50 > (i + offset_x + 48 + 20) >= 0:
                    array[j][i + 48 + offset_x + 20] = decoder(buffer[j + RIGHT_OFFESET])

                if (50 > (i + prev_x_v + 48 + 20) >= 0) and (abs(prev_x_v - offset_x) > 1):
                    if x_bool:
                        if (screen_x > 145 or screen_x < 71):#and buffer[j + RIGHT_OFFESET] != 'c':
                            array[j][i + 48 + prev_x_v + 20] = decoder("c")
                    else:
                        if (screen_x < 71 and buffer[j + RIGHT_OFFESET] != 'c'):
                            array[j][i + 48 + prev_x_v + 20] = decoder("g")
                        elif screen_x > 145:
                            array[j][i + 48 + prev_x_v + 20] = decoder("c")


def drow_car(x, y, array, angle) -> None:
    for i in range(5):
        for j in range(5):
            array[int(y) + j - 2][int(x) + i - 2] = "\033[94m" + '9' + "\033[0m"
            
    array[int(y)][int(x)] = "\033[94m" + '+' + "\033[0m"


def mov_car(x: float, y: float, angle: int) -> tuple[float, float, int, str]:
    go: str = " "
    new_x, new_y, new_angle = x, y, angle
    if keyboard.is_pressed('w'):
        go = "f"
    elif keyboard.is_pressed('s'):
        go = "r"

    if keyboard.is_pressed('a'):
        new_angle += ANGLE
        if new_angle >= 360:
            new_angle -= 360  # Mantém o ângulo no intervalo 0-359

    elif keyboard.is_pressed('d'):
        new_angle -= ANGLE
        if new_angle < 0:
            new_angle += 360

    return new_x, new_y, new_angle, go


async def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


async def main():
    screen_x, screen_y = 20, 20
    angle = 180
    go = " "
    screen_x, screen_y, x_v, y_v = mov_screen(screen_x, screen_y, angle, go)
    car_x, car_y = 24, 24
    prev_x_v, prev_y_v = x_v, y_v
    angle_prev = 10
    Buffer: list[str] = ['c'] * SIZE_BUFFER
    array: list[list[int]] = [([0] * 50) for _ in range(50)]

    try:
        while True:
            if x_v != prev_x_v or y_v != prev_y_v or angle_prev != angle:
                await asyncio.sleep(0.1)
                await clear()

                aux_prev_x_v = (prev_x_v - 1) if (prev_x_v < x_v) else (prev_x_v + 1)
                aux_prev_y_v = (prev_y_v - 1) if prev_y_v < y_v else (prev_y_v + 1)

                draw_track(int(screen_x), int(screen_y), Buffer)
                simularTela(Buffer, array, int(x_v), int(y_v), int(aux_prev_x_v), int(aux_prev_y_v), prev_x_v < x_v, prev_y_v < y_v, int(screen_x), int(screen_y))
                drow_car(car_x, car_y, array, angle)
                print(Buffer[LEFT_OFFESET:LEFT_OFFESET+50])
                print(f"coordenadas  x_h = {int(screen_x)}, y_h = {int(screen_y)}, x_v = {int(x_v)}, y_v = {int(y_v)} e prev_x_v = {int(aux_prev_x_v)}, prev_y_v = {int(aux_prev_y_v)}")
                print(f"coordenadas car x = {car_x}, car y = {car_y}, angulo {angle} e x_v = {x_v} e y_v = {y_v} and {abs(aux_prev_x_v - x_v) > 1} and {abs(aux_prev_y_v - y_v) > 1}")
                for i in range(50):
                    for j in range(50):
                        print(array[i][j], end=" ")
                    print()

            prev_x_v = x_v
            prev_y_v = y_v
            angle_prev = angle
            car_x, car_y, angle, go = mov_car(car_x, car_y, angle)
            if go != " ":
                screen_x, screen_y, x_v, y_v = mov_screen(screen_x, screen_y, angle, go)

    except KeyboardInterrupt:
        await clear()
        print("Fim da execução")

asyncio.run(main())
