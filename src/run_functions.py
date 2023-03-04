'''Run helper functions'''
# pylint: disable=line-too-long, import-error
# flake8: noqa: E501

from datetime import datetime, timedelta
from src.classes import Entrenamiento, Saltos, CicloDeEntrenamiento
from src.errors import DataError, CommandError, NoDataError, NumDataError, NoValidTimeError


def print_training(training, nest=0):
    '''Print training to the console'''
    space = ''
    if nest > 0:
        space = '   ' * nest

    for num, trng in enumerate(training, start=1):
        if isinstance(trng, Entrenamiento):
            print(f'{space}{num}: {trng}')
        elif isinstance(trng, CicloDeEntrenamiento):
            print(f'{space}{num}:')
            print_training(trng, nest + 1)
    print(
        f'{space}Tiempo Total: {training.get_time()}, Repeticiones: {training.get_reps()}')

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
    if data[0] in ('5', '7', '12'):
        try:
            tmp_train = Saltos(*split_jump_data(data))
        except ValueError as error:
            raise NumDataError from error
        except ArithmeticError as error:
            raise NoValidTimeError from error
    elif data[0] == ('10'):
        try:
            tmp_train = Entrenamiento(*data)
        except TypeError as error:
            raise NumDataError from error
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
        if comm in ['s', 'i', 'f', 'e', 'c', 'w', 'd', 't', 'h', 'g', 'r', 'a']:
            return comm
        raise CommandError
    elif len(splt_data) == 1 and comm.isdigit() and len(comm) == 2:
        if comm == '10':
            return ['10', '50', '60', '1']
        raise CommandError
    elif len(splt_data) in (4, 5):
        return splt_data
    raise NumDataError


def split_data_simple(data):
    '''Splits data by space and return data for training'''
    splt_data = data.split()
    if len(splt_data) in (4, 5):
        return splt_data
    raise NumDataError
