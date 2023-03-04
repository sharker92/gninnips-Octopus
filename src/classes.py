'''Module clases'''
# pylint: disable=line-too-long, import-error
# flake8: noqa: E501
from datetime import datetime, timedelta
from src.descriptors import MinMaxRange, IsTime
from src.errors import DataError, RangeError


class Entrenamiento():
    '''Class Entrenamiento'''

    training = MinMaxRange(1, 12)
    hearth_rate = MinMaxRange(50, 90)
    cadence = MinMaxRange(60, 120)
    tot_time = IsTime()

    def __init__(self, training, hearth_rate, cadence, tot_time):
        self.training = training
        self.hearth_rate = hearth_rate
        self.cadence = cadence
        self.tot_time = tot_time

    def get_training(self):
        '''Get training attribute'''
        return self.training

    def get_hearth_rate(self):
        '''Get hearth_rate attribute'''
        return str(self.hearth_rate)

    def get_cadence(self):
        '''Get cadence attribute'''
        return str(self.cadence)

    def get_tot_time_str(self):
        '''Get tot_time in string'''
        if self.tot_time.minute == 0:
            try:
                return self.tot_time.strftime('%-S"')
            except ValueError:
                return self.tot_time.strftime('%#S"')
        elif self.tot_time.second == 0:
            try:
                return self.tot_time.strftime('%-M\'')
            except ValueError:
                return self.tot_time.strftime('%#M\'')
        else:
            try:
                return self.tot_time.strftime('%-M\'%-S"')
            except ValueError:
                return self.tot_time.strftime('%#M\'%#S"')

    def __eq__(self, other_obj):
        return (self.training == other_obj.training and
                self.hearth_rate == other_obj.hearth_rate and
                self.cadence == other_obj.cadence and
                self.tot_time == other_obj.tot_time)

    def __str__(self):
        # Al imprimir la instancia en el descriptor provoca un error de atributo por aun no estar definidos todos los valores.
        try:
            if self.training == 10:
                return f'T: {self.training}, :D'
            else:
                return f'T: {self.training}, {self.hearth_rate}%, \
{self.cadence}rpm, {datetime.strftime(self.tot_time, "%-M:%-S")}'
        except AttributeError:
            return object.__str__(self)
        except ValueError:
            return f'T: {self.training}, {self.hearth_rate}%, \
{self.cadence}rpm, {datetime.strftime(self.tot_time, "%#M:%#S")}'

    def __repr__(self):
        try:
            return f'{self.training} {self.hearth_rate} \
{self.cadence} {datetime.strftime(self.tot_time, "%-M:%-S")}'
        except AttributeError:
                return object.__repr__(self)
        except ValueError:
            return f'{self.training} {self.hearth_rate} \
{self.cadence} {datetime.strftime(self.tot_time, "%#M:%#S")}'


class Saltos(Entrenamiento):
    '''Saltos Class'''
    cadence_up = MinMaxRange(60, 120)
    time_dwn = IsTime()
    time_up = IsTime()

    def __init__(self, training, hearth_rate, cadence, tot_time, cadence_up, time_dwn, time_up):
        super().__init__(training, hearth_rate, cadence, tot_time)
        self.cadence_up = cadence_up
        self.time_dwn = time_dwn
        self.time_up = time_up

    def get_cadence(self):
        '''Get cadence intervals attributes'''
        return f'{self.cadence}/{self.cadence_up}'

    def get_num_jump(self):
        '''Get number of jumps'''

        tot_time_delta = timedelta(
            minutes=self.tot_time.minute, seconds=self.tot_time.second)
        num_jumps = tot_time_delta / (timedelta(seconds=self.time_dwn.second) +
                                      timedelta(seconds=self.time_up.second))
        return f'{int(num_jumps)}'

    def get_time_str(self):
        '''Return time intervals in string'''
        try:
            return f'{self.time_dwn.strftime("%-S")}"/{self.time_up.strftime("%-S")}"'
        except ValueError:
            return f'{self.time_dwn.strftime("%#S")}"/{self.time_up.strftime("%#S")}"'

    def __eq__(self, other_obj):
        return (self.training == other_obj.training and
                self.hearth_rate == other_obj.hearth_rate and
                self.cadence == other_obj.cadence and
                self.tot_time == other_obj.tot_time and
                self.cadence_up == other_obj.cadence_up and
                self.time_dwn == other_obj.time_dwn and
                self.time_up == other_obj.time_up)

    def __str__(self):
        # Al imprimir la instancia en el descriptor provoca un error de atributo por aun no estar definidos todos los valores.
        try:
            return f'T: {self.training}, \
{self.hearth_rate}%, {self.cadence}/{self.cadence_up}rpm, \
{datetime.strftime(self.tot_time, "%-M:%-S")}, \
{datetime.strftime(self.time_dwn, "%-S")}/\
{datetime.strftime(self.time_up, "%-S")}'
        except AttributeError:
            return object.__str__(self)
        except ValueError:
            return f'T: {self.training}, \
{self.hearth_rate}%, {self.cadence}/{self.cadence_up}rpm, \
{datetime.strftime(self.tot_time, "%#M:%#S")}, \
{datetime.strftime(self.time_dwn, "%#S")}/\
{datetime.strftime(self.time_up, "%#S")}'

    def __repr__(self):
        try:
            return f'{self.training} {self.hearth_rate} {self.cadence}/{self.cadence_up} \
{datetime.strftime(self.tot_time, "%-M:%-S")}  \
{datetime.strftime(self.time_dwn, "%-M:%-S")}/\
{datetime.strftime(self.time_up, "%-M:%-S")}'
        except AttributeError:
            return object.__repr__(self)
        except ValueError:
            return f'{self.training} {self.hearth_rate} {self.cadence}/{self.cadence_up} \
{datetime.strftime(self.tot_time, "%#M:%#S")}  \
{datetime.strftime(self.time_dwn, "%#M:%#S")}/\
{datetime.strftime(self.time_up, "%#M:%#S")}'


class CicloDeEntrenamiento():
    '''Clase de la Clase'''
    repetitions = MinMaxRange(1, 100)

    def __init__(self):
        self.training_list = list()
        self.tot_class_time = timedelta()
        self.repetitions = 1

    def __iter__(self):
        return iter(self.training_list)

    def calc_time(self):
        '''Calculates the total time of the training.'''
        self.tot_class_time = timedelta()
        for trng in self.training_list:
            if isinstance(trng, Entrenamiento):
                self.tot_class_time += timedelta(
                    minutes=trng.tot_time.minute,
                    seconds=trng.tot_time.second)
            elif isinstance(trng, CicloDeEntrenamiento):
                self.tot_class_time += trng.tot_class_time
        self.tot_class_time *= self.repetitions

    def add_training(self, trnng_object):
        '''Add trainings to the list'''
        if isinstance(trnng_object, (Entrenamiento, CicloDeEntrenamiento)):
            self.training_list.append(trnng_object)
            self.calc_time()
        else:
            raise DataError(trnng_object)

    def remove_training(self, pos=-1):
        '''remove training in the position indicated'''
        if pos < 1 or pos > len(self.training_list):
            raise RangeError(1, len(self.training_list))
        pos -= 1
        rmvd_trnng = self.training_list.pop(pos)
        self.calc_time()
        return rmvd_trnng

    def insert_training(self, trnng_object, pos=-1):
        '''Insert training in the position indicated'''
        if isinstance(trnng_object, (Entrenamiento, CicloDeEntrenamiento)):
            self.training_list.insert(pos, trnng_object)
            self.calc_time()
        else:
            raise DataError(trnng_object)

    def change_training(self, sel1, sel2):
        '''change of position elements on training_list'''
        self.training_list[sel1], self.training_list[sel2] = self.training_list[sel2], self.training_list[sel1]

    def check_if_cycle(self, sel):
        '''check if training_list element is a cycle and return it'''
        if isinstance(self.training_list[sel], Entrenamiento):
            return False
        elif isinstance(self.training_list[sel], CicloDeEntrenamiento):
            return self.training_list[sel]

    def edit_training(self, trnng_object, sel):
        '''Edit training element'''
        self.training_list[sel] = trnng_object
        self.calc_time()

    def reps(self, reps):
        '''updates the repetitions value'''
        self.repetitions = reps
        self.calc_time()

    def get_time(self):
        '''returns total time'''
        time_str = str(self.tot_class_time)
        if time_str[0] == '0':
            return time_str[2:]
        else:
            return str(self.tot_class_time)

    def get_reps(self):
        '''returns repetitions'''
        return str(self.repetitions)

    def __len__(self):
        return len(self.training_list)

    def __str__(self):
        base = ''
        for i, trn in enumerate(self.training_list):
            base += f'{i+1}: {trn}\n'
        return f'{base}Total time: {self.tot_class_time}, Repetitions: {self.repetitions}'

    def __repr__(self):
        return f'<{self.training_list}\nTotal time: {self.tot_class_time}, Repetitions: {self.repetitions}>'

    def get_cmnd_track(self):
        '''returns string with the commands to build the training'''
        trnng_track = list()
        trnng_track.append(['I'])
        for trnng in self.training_list:
            if isinstance(trnng, CicloDeEntrenamiento):
                trnng_track += trnng.get_cmnd_track()
            else:
                trnng_track.append(repr(trnng).split())
        trnng_track.append(['F', self.repetitions])
        return trnng_track

    def __add__(self, other):
        if isinstance(other, CicloDeEntrenamiento):
            new_training_list = self.training_list + other.training_list
            new_cycle = CicloDeEntrenamiento()
            for trnng in new_training_list:
                new_cycle.add_training(trnng)
            return new_cycle
        else:

            return None
