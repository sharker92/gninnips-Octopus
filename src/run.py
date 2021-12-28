'''Run Module'''
# pylint: disable=line-too-long, import-error
# flake8: noqa: E501
import sys
import os
from datetime import date
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from src.classes import Entrenamiento, Saltos, CicloDeEntrenamiento
from src.errors import DataError, InputDataError, CommandError, NoDataError, NumDataError, NoValidTimeError, RangeError


FORMAT = '''
Formato de comandos:

Comando:
<Letra_del_comando >

Entrenamiento:
<  # Entrenamiento> <% 100> <Cadencia 000> <Tiempo 00:00>

Saltos:
<  # Entrenamiento> <% 100> <Cadencia 000/000> <Tiempo Total 00:00> <Tiempo Saltos 00/00>'''

BASE_QUESTION = '''
Ingrese el entrenamiento o comando deseado: '''

EDIT_QUESTION = '''
Ingrese el entrenamiento sustituto: '''

COMMAND_MESSAGE = f'''
Comandos:

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
{FORMAT}
'''

EDIT_MESSAGE = '''
Editando entrenamiento {num}.
{format}
'''


def convert_to_time(time):
    '''Convert strings to time'''
    try:
        return datetime.strptime(time, '%M:%S')
    except ValueError:
        try:
            return datetime.strptime(time, '%S')
        except ValueError as error:
            raise DataError(time) from error


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
    img_width = 1270
    img_length = 820
    img = Image.new('RGB', (img_width, img_length), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype(
        resource_path("./images/HelveticaNeueBold.ttf"), 75)
    font_tot_time = ImageFont.truetype(
        resource_path("./images/HelveticaNeueBold.ttf"), 30)
    logo = Image.open(resource_path('./images/logo.jpeg'))
    size = (150, 150)
    logo.thumbnail(size)
    img.paste(logo, (0, 0))
    x_title = center_text(img_width, titulo, draw, font_title)
    draw.text((x_title, 0), titulo, 0, font=font_title)
    x_date = img_width - 180
    draw.text((x_date, 0), fecha.strftime("%d/%m/%Y"), 0, font=font_tot_time)
    x_time = img_width - 155
    draw.text((x_time, 30), training.get_time(), 0, font=font_tot_time)
    lst_images = list()
    for i in range(1, 10):
        tmp_img = Image.open(resource_path(f'./images/{i}.png'))
        size = (100, 100)
        tmp_img.thumbnail(size)
        lst_images.append(tmp_img)

    draw_training(img, draw, training, lst_images)
    print('Imagen guardada en:')
    img.save(save_path(f'{fecha.strftime("%d-%m-%Y")}.jpg'))


def draw_training(img, draw, training, lst_images, eje_x=90, eje_y=150):
    '''Recursive drawing cycle'''
    margin_x = eje_x
    margin_y = 180
    img_limit = 1170
    box_size = 100
    font = ImageFont.truetype(resource_path(
        "./images/HelveticaNeueBold.ttf"), 25)
    bracket_font = ImageFont.truetype(
        resource_path("./images/HelveticaNeueRegular.ttf"), 150)
    for trng in training:
        if isinstance(trng, CicloDeEntrenamiento):
            eje_x += 10
            y_cntrd = 45
            draw.text((eje_x - 75, eje_y - y_cntrd), '[',
                      font=bracket_font, fill=(255, 0, 0), stroke_width=3)
            eje_x, eje_y = draw_training(
                img, draw, trng, lst_images, eje_x, eje_y)
            end_text = f']x{trng.get_reps()}'
            end_text_lngth = int(draw.textlength(end_text, font=bracket_font))
            if eje_x + end_text_lngth - 160 > img_limit:
                eje_x = margin_x
                eje_y += 180
            draw.text((eje_x - 60, eje_y - y_cntrd), end_text,
                      font=bracket_font, fill=(255, 0, 0), stroke_width=3)
            eje_x += int(end_text_lngth - 160)

        elif isinstance(trng, Entrenamiento):
            img.paste(lst_images[trng.get_training() - 1], (eje_x, eje_y))
            draw.text((eje_x - 50, eje_y + 25), f'{trng.get_hearth_rate()}%',
                      0, font=font)
            x_cntrd = center_text(
                box_size, trng.get_cadence(), draw, font)
            draw.text((eje_x + x_cntrd, eje_y - 30), trng.get_cadence(),
                      0, font=font)
            if isinstance(trng, Saltos):
                x_cntrd = center_text(
                    box_size, trng.get_time_str(), draw, font)
                draw.text((eje_x + x_cntrd, eje_y + 90),
                          trng.get_time_str(),  0, font=font)
                x_cntrd = center_text(
                    box_size, trng.get_num_jump(), draw, font)
                draw.text((eje_x + x_cntrd, eje_y + 30),
                          trng.get_num_jump(), 0, font=font)
            else:
                x_cntrd = center_text(
                    box_size, trng.get_tot_time_str(), draw, font)
                draw.text((eje_x + x_cntrd, eje_y + 90),
                          trng.get_tot_time_str(), 0, font=font)

        eje_x += 160
        if eje_x > img_limit:
            eje_x = margin_x
            eje_y += margin_y
    return eje_x, eje_y


def center_text(width, text, draw, font):
    '''returns location for center text'''
    centered_text_location = width/2 - draw.textlength(text, font=font)/2
    return centered_text_location


def print_training(training, nest=0):
    '''Print training to the console'''
    space = ''
    if nest > 0:
        space = '   ' * nest

    for num, trng in enumerate(training):
        num += 1
        if isinstance(trng, Entrenamiento):
            print(f'{space}{num}: {trng}')
        elif isinstance(trng, CicloDeEntrenamiento):
            print(f'{num}:')
            print_training(trng, nest + 1)
    print(
        f'{space}Tiempo Total: {training.get_time()}, Repeticiones: {training.get_reps()}')


def run():
    '''Run main program'''
    titulo = ''
    fecha = date.today()
    history_lst = list()
    history_lst.append(CicloDeEntrenamiento())
    current_elem = len(history_lst) - 1
    while True:
        for lst in history_lst:
            lst.calc_time()
        print('#'*40)
        print('Entrenamiento:\n')
        print_training(history_lst[0])
        print(COMMAND_MESSAGE)
        inpt_data = input(BASE_QUESTION)
        print()
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
            if current_elem == 0:
                print('No es posible salir del ciclo principal.\nIntente otra opción')
                continue
            try:
                reps = input('Indique el número de repeticiones: ')
                history_lst[current_elem].reps(reps)
            except RangeError as error:
                print(error)
                continue
            except DataError as error:
                print(error)
                continue
            print('Saliendo del ciclo.')
            history_lst.pop()
            current_elem = len(history_lst) - 1
            continue
        elif splt_data == 'e':
            if len(history_lst[current_elem]) == 0:
                print('El ciclo no tiene elementos.\nIntente otra opción.')
                continue
            try:
                sel = input('Seleccione un elemento a editar: ')
                sel = int(sel) - 1
                if sel < 0 or sel >= len(history_lst[current_elem]):
                    raise RangeError(1, len(history_lst[current_elem]))
            except RangeError as error:
                print(error)
                continue
            except ValueError as error:
                try:
                    raise DataError(sel) from error
                except DataError as error:
                    print(error)
                    continue

            temp_train = history_lst[current_elem].check_if_cycle(sel)
            if temp_train:
                print('Editando ciclo de entrenamiento.')
                history_lst.append(temp_train)
                current_elem = len(history_lst) - 1
            else:
                print(EDIT_MESSAGE.format(num=sel + 1, format=FORMAT))
                inpt_data = input(EDIT_QUESTION)
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
                    input('¿Por cuál elemento desea intercambiarlo?: ')) - 1
                if sel2 < 0 or sel2 >= len(history_lst[current_elem]):
                    raise RangeError(1, len(history_lst[current_elem]))
            except RangeError as error:
                print(error)
                continue
            history_lst[current_elem].change_training(sel1, sel2)
            print(f'Elementos {sel1+1} y {sel2+1} intercambiados.')
            continue
        elif splt_data == 'd':
            if not history_lst[current_elem]:
                print('No hay elementos que eliminar en este ciclo.')
                continue
            try:
                sel = int(input('Ingrese elemento a eliminar: '))
                deleted = history_lst[current_elem].remove_training(sel)
            except RangeError as error:
                print(error)
                continue
            except ValueError as error:
                try:
                    raise DataError(sel) from error
                except DataError as error:
                    print(error)
                    continue
            print(f'Elemento "{sel}: {deleted}" eliminado.')
            continue
        elif splt_data == 'h':
            fecha = input(
                'Por favor ingrese la fecha del entrenamiento (dd/mm/aa): ')
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
        # pylint: disable=protected-access
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def save_path(relative_path):
    '''Get absolute path to save file for PyInstaller'''
    try:
        # PyInstaller add frozen to sys
        # pylint: disable=pointless-statement
        sys.frozen
        base_path = os.path.dirname(sys.executable)
    except AttributeError:
        base_path = os.path.abspath(".")
    print(os.path.join(base_path, relative_path))
    return os.path.join(base_path, relative_path)
