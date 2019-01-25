from settings import VERBACO_CFILE, VARIABLE_MAP, CATEGORY_MAP, OUTPUT_CFILE
from collections import namedtuple, defaultdict

class UpdateCommand:

    SQL_START = 'UPDATE VDATA SET '

    def __init__(self, input_line):
        self.input_line = input_line
        start = len(UpdateCommand.SQL_START)
        assignments_string, criteria = self.input_line[start:].split(' WHERE ')
        var, serial = criteria.split('=')
        self.respondent_variable = var.strip()
        self.serial = int(serial.strip())
        self.assignments = [
            Assignment(a)
            for a in assignments_string.strip().split(', ')
            ]

    def update_variables(self, variable_map):
        for a in self.assignments:
            a.variable = variable_map.get(a.variable, a.variable)

    def update_codes(self, category_map):
        for a in self.assignments:
            code_map = category_map.get(a.variable)
            if code_map:
                a.codes = [code_map.get(c, c) for c in a.codes]

    def update_serial(self, func):
        self.serial = func(self.serial)

    @property
    def text(self):
        return f'{UpdateCommand.SQL_START}{",".join(a.text for a in self.assignments)} WHERE {self.respondent_variable}={self.serial}'

class Assignment:

    def __init__(self, input_line):
        raw_variable, raw_codes = input_line.split('=')
        self.variable = raw_variable.strip()
        self.codes = raw_codes[1:-1].strip().split(',')

    @property
    def text(self):
        return f'{self.variable}={{{",".join(self.codes)}}}'

def read_variable_map(path):
    with open(path, mode='r', encoding='utf-8') as f:
        variable_map = {}
        for row in f:
            old_variable, new_variable = row.strip('\n').split(',')
            variable_map[old_variable] = new_variable
        return variable_map

def read_category_map(path):
    with open(path, mode='r', encoding='utf-8') as f:
        category_map = defaultdict(dict)
        for row in f:
            variable, old_code, new_code = row.strip('\n').split(',')
            category_map[variable][old_code] = new_code
        return category_map


# main

vm = read_variable_map(VARIABLE_MAP)
cm = read_category_map(CATEGORY_MAP)


with open(OUTPUT_CFILE, mode='w', encoding='utf-8') as new:
    with open(VERBACO_CFILE, mode='r', encoding='utf-8') as f:
        for row in f:
            statement = UpdateCommand(row)
            statement.update_codes(cm)
            statement.update_variables(vm)
            new.write(statement.text + '\n')
