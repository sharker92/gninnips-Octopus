'''Run Module'''
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from src.classes import Entrenamiento, Saltos, CicloDeEntrenamiento
from src.errors import DataError, InputDataError, CommandError, NoDataError, NumDataError, NoValidTimeError, RangeError
from datetime import date
import sys
import os
BASE_MESSAGE = '''
Ingrese el entrenamiento en el siguiente formato:

<#Entrenamiento> <% 100> <Cadencia 000> <Tiempo 00:00>

Saltos:

<#Entrenamiento> <% 100> <Cadencia 000/000> <Tiempo Total 00:00> <Tiempo Saltos 00/00>

1 -> Terreno Plano Sentado
2 -> Terreno Plano de Pie
3 -> Escalada Sentado
4 -> Carrera con resistencia
5 -> Saltos
6 -> Escalada de Pie
7 -> Saltos en Colina
8 -> Sprint Sentado
9 -> Sprint en Colina
I -> Iniciar Ciclo
F -> Finalizar Ciclo
E -> Editar Entrenamiento
C -> Cambiar orden
D -> Eliminar entrenamiento
T -> Cambiar Titulo
H -> Cambiar Fecha
G -> Generar imagen
S -> Salir

'''

EDIT_MESSAGE = '''
Editando entrenamiento {num}.
Ingrese el entrenamiento en el siguiente formato:

<#Entrenamiento> <% 100> <Cadencia 000> <Tiempo 00:00>

Saltos:

<#Entrenamiento> <% 100> <Cadencia 000/000> <Tiempo Total 00:00> <Tiempo Saltos 00/00>
'''


def convert_to_time(tm):
    '''Convert strings to time'''
    try:
        return datetime.strptime(tm, '%M:%S')
    except ValueError:
        try:
            return datetime.strptime(tm, '%S')
        except ValueError:
            raise DataError(tm)


def check_coherent_time(tm_tot, tm_dwn, tm_up):
    '''Check if total time is divisible between time down plus time up'''
    tm_tot = convert_to_time(tm_tot)
    tm_dwn = convert_to_time(tm_dwn)
    tm_up = convert_to_time(tm_up)
    dlt_tot = timedelta(minutes=tm_tot.minute, seconds=tm_tot.second)
    dlt_dwn = timedelta(minutes=tm_dwn.minute, seconds=tm_dwn.second)
    dlt_up = timedelta(minutes=tm_up.minute, seconds=tm_up.second)
    return not (dlt_tot / (dlt_dwn + dlt_up)).is_integer()


def split_jump_data(data):
    '''Splits Saltos Data preparing it for Saltos Class'''
    tmp_trnng = data[0]
    tmp_hrth_rate = data[1]
    tmp_cad_dwn, tmp_cad_up = data[2].split('/')
    tmp_tot_tme = data[3]
    tmp_tme_dwn, tmp_tme_up = data[4].split('/')
    if check_coherent_time(tmp_tot_tme, tmp_tme_dwn, tmp_tme_up):
        raise ArithmeticError
    return tmp_trnng, tmp_hrth_rate, tmp_cad_dwn, tmp_tot_tme, tmp_cad_up, tmp_tme_dwn, tmp_tme_up


def create_trnng_obj(data):
    '''Creates the indicated training object'''
    if data[0] in ('5', '7'):
        try:
            tmp_train = Saltos(*split_jump_data(data))
        except ValueError as error:
            raise NumDataError from error
        except ArithmeticError as error:
            raise NoValidTimeError from error
    else:
        try:
            tmp_train = Entrenamiento(*data)
        except TypeError as error:
            raise NumDataError from error
    return tmp_train


def split_data(data):
    '''splits data by space and return command or data for training'''
    splt_data = data.split()
    try:
        comm = splt_data[0]
    except IndexError as error:
        raise NoDataError from error

    if len(splt_data) == 1 and comm.isalpha() and len(comm) == 1:
        comm = comm.lower()
        if comm in ['s', 'i', 'f', 'e', 'c', 'd', 't', 'h', 'g']:
            return comm
        raise CommandError
    if len(splt_data) in (4, 5):
        return splt_data
    raise NumDataError


def split_data_simple(data):
    '''splits data by space and return data for training'''
    splt_data = data.split()
    if len(splt_data) in (4, 5):
        return splt_data
    raise NumDataError


def generate_image(training, fecha, titulo=''):
    '''Convert training to jpeg'''
    img = Image.new('RGB', (1000, 720), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype(
        resource_path("./images/Arial Unicode.ttf"), 75)
    font_tot_time = ImageFont.truetype(
        resource_path("./images/Arial Unicode.ttf"), 30)
    logo = Image.open(resource_path('./images/logo.jpeg'))
    size = (150, 150)
    logo.thumbnail(size)
    img.paste(logo, (0, 0))
    # titulo = 'Día de la carrera larga'
    # print(draw.textlength('Día de la carrera larga', font=font))
    draw.text((175, 0), titulo, 0, font=font_title)
    draw.text((830, 90), fecha, 0, font=font_tot_time)
    draw.text((855, 120), training.get_time(), 0, font=font_tot_time)
    lst_images = list()
    for i in range(1, 10):
        tmp_img = Image.open(resource_path(f'./images/{i}.png'))
        size = (100, 100)
        tmp_img.thumbnail(size)
        lst_images.append(tmp_img)
    draw_training(img, draw, training, lst_images)
    img.save(save_path(f'{fecha}.jpg'))


def draw_training(img, draw, training, lst_images, eje_x=70, eje_y=200):
    '''Recursive drawing cycle'''
    font = ImageFont.truetype(resource_path("./images/Arial Unicode.ttf"), 25)
    bracket_font = ImageFont.truetype(
        resource_path("./images/Arial Unicode.ttf"), 125)
    for trng in training:
        if isinstance(trng, Saltos):
            img.paste(lst_images[trng.get_training() - 1], (eje_x, eje_y))
            draw.text((eje_x - 50, eje_y + 25), f'{trng.get_hearth_rate()}%',
                      0, font=font, stroke_width=1)
            draw.text((eje_x + 6, eje_y - 30), trng.get_cadence(),
                      0, font=font, stroke_width=1)
            draw.text((eje_x + 10, eje_y + 90), trng.get_time(),
                      0, font=font, stroke_width=1)
            draw.text((eje_x + 40, eje_y + 30), trng.get_num_jump(),
                      0, font=font, stroke_width=1)
        elif isinstance(trng, Entrenamiento):
            img.paste(lst_images[trng.get_training() - 1], (eje_x, eje_y))
            draw.text((eje_x - 50, eje_y + 25), f'{trng.get_hearth_rate()}%',
                      0, font=font, stroke_width=1)
            draw.text((eje_x + 30, eje_y - 30), trng.get_cadence(),
                      0, font=font, stroke_width=1)
            draw.text((eje_x + 15, eje_y + 90), trng.get_tot_time(),
                      0, font=font, stroke_width=1)
        elif isinstance(trng, CicloDeEntrenamiento):
            eje_x += 10
            draw.text((eje_x - 75, eje_y - 55), '[',
                      font=bracket_font, fill=(255, 0, 0))
            eje_x, eje_y = draw_training(
                img, draw, trng, lst_images, eje_x, eje_y)
            draw.text((eje_x - 60, eje_y - 55), f']x{trng.get_reps()}',
                      font=bracket_font, fill=(255, 0, 0))
            eje_x += 10
        eje_x += 160
        if eje_x > 880:
            eje_x = 70
            eje_y += 180
    return eje_x, eje_y


def print_training(training, nest=0):
    '''print training to the console'''
    space = ''
    if nest > 0:
        space = "   " * nest

    for num, trng in enumerate(training):
        num += 1
        if isinstance(trng, Entrenamiento):
            print(f'{space}{num}: {trng}')
        elif isinstance(trng, CicloDeEntrenamiento):
            print(f'{num}:')
            print_training(trng, nest + 1)
    print(
        f'{space}Total time: {training.get_time()}, Repetitions: {training.get_reps()}')


def run():
    '''Run main program'''
    titulo = ''
    fecha = str(date.today())
    history_lst = list()
    history_lst.append(CicloDeEntrenamiento())
    current_elem = len(history_lst) - 1
    while True:
        for lst in history_lst:
            lst.calc_time()
        print_training(history_lst[0])
        inpt_data = input(BASE_MESSAGE)
        try:
            splt_data = split_data(inpt_data)
        except InputDataError as error:
            print(error)
            continue
        if splt_data == 's':
            print("Saliendo...")
            break
        elif splt_data == 'i':
            print('Iniciando nuevo ciclo.')
            new_train_cicle = CicloDeEntrenamiento()
            history_lst.append(new_train_cicle)
            history_lst[current_elem].add_training(new_train_cicle)
            current_elem = len(history_lst) - 1
            continue
        elif splt_data == 'f':
            print('Saliendo del ciclo.')
            if current_elem == 0:
                print('No es posible salir del ciclo principal.\nIntente otra opción')
                continue
            try:
                reps = input('Indique el número de repeticiones: ')
                history_lst[current_elem].reps(reps)
            except RangeError as error:
                print(error)
                continue
            history_lst.pop()
            current_elem = len(history_lst) - 1
            continue
        elif splt_data == 'e':
            if len(history_lst[current_elem]) == 0:
                print('El ciclo no tiene elementos.\nIntente otra opción')
                continue
            try:
                sel = int(input('Seleccione un elemento a editar: ')) - 1
                if sel < 0 or sel >= len(history_lst[current_elem]):
                    raise RangeError(1, len(history_lst[current_elem]))
            except RangeError as error:
                print(error)
                continue
            temp_train = history_lst[current_elem].check_if_cycle(sel)
            print(temp_train)
            if temp_train:
                print('Editando ciclo de entrenamiento.')
                history_lst.append(temp_train)
                current_elem = len(history_lst) - 1
            else:
                inpt_data = input(EDIT_MESSAGE.format(num=sel))
                try:
                    splt_data = split_data(inpt_data)
                except InputDataError as error:
                    print(error)
                    continue
                try:
                    tmp_train = create_trnng_obj(splt_data)
                except InputDataError as error:
                    print(error)
                    continue
                history_lst[current_elem].edit_training(tmp_train, sel)

            continue
        elif splt_data == 't':
            titulo = input('Por favor ingrese el titulo del entrenamiento: ')
            print(f'El nuevo titulo es:\n{titulo}')
        elif splt_data == 'c':
            try:
                sel1 = int(input('Ingrese elemento a cambiar de lugar: ')) - 1
                if sel1 < 0 or sel1 >= len(history_lst[current_elem]):
                    raise RangeError(1, len(history_lst[current_elem]))
            except RangeError as error:
                print(error)
                continue
            try:
                sel2 = int(
                    input('¿Por cual elemento desea intercambiarlo?: ')) - 1
                if sel2 < 0 or sel2 >= len(history_lst[current_elem]):
                    raise RangeError(1, len(history_lst[current_elem]))
            except RangeError as error:
                print(error)
                continue
            history_lst[current_elem].change_training(sel1, sel2)
            continue
        elif splt_data == 'd':
            if not history_lst[current_elem]:
                print('No hay elementos que eliminar en este ciclo.')
                continue
            try:
                sel = int(input('Ingrese elemento a eliminar: '))
                history_lst[current_elem].remove_training(sel)
            except RangeError as error:
                print(error)
                continue
            except ValueError as error:
                try:
                    raise DataError(sel) from error
                except DataError as error:
                    print(error)
                    continue
            continue
        elif splt_data == 'h':
            fecha = input(
                'Por favor ingrese la fecha del entrenamiento (01/12/22): ')
            try:
                fecha = datetime.strptime(fecha, '%d/%m/%y')
                print(f'La nueva fecha es:\n{fecha.strftime("%d/%m/%Y")}')
            except ValueError:
                print(
                    f'Fecha ingresada no valida {fecha}.\nPor favor intentelo de nuevo.')
            continue
        elif splt_data == 'g':
            generate_image(history_lst[0], fecha, titulo)
            continue
        try:
            tmp_train = create_trnng_obj(splt_data)
        except InputDataError as error:
            print(error)
            continue

        history_lst[current_elem].add_training(tmp_train)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def save_path(relative_path):
    '''Get absolute path to save file for PyInstaller'''
    try:
        sys.frozen
        base_path = os.path.dirname(sys.executable)
    except AttributeError:
        base_path = os.path.abspath(".")
    print(os.path.join(base_path, relative_path))
    return os.path.join(base_path, relative_path)
