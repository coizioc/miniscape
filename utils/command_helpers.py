# This file should be free of any project-specific imports. Non-project imports (like stdlib, 3rd party) should be fine
import datetime
import math
from typing import Tuple


def parse_number_and_name(args):
    """Parses the number and item name from an arbitrary number of arguments."""
    if len(args) == 0:
        number = None
        name = None
    elif len(args) == 1:
        number = 1
        name = args[0]
    else:
        try:
            number = parse_int(args[0])
            name = ' '.join(args[1:])
        except ValueError:
            number = 1
            name = ' '.join(args)
    return number, name


def parse_number_name_length(args):
    """Parses arguments of the form [number] [name] [length]."""
    if args:
        try:
            number = parse_int(args[0])
            name = ' '.join(args[1:])
            length = None
        except ValueError:
            number = None
            try:
                name = ' '.join(args[:-1])
                length = parse_int(args[-1])
            except ValueError:
                name = ' '.join(args)
                length = None
        return number, name, length
    else:
        return None, None, None


def parse_int(number_as_string):
    """Converts an string into an int if the string represents a valid integer"""
    if type(number_as_string) == tuple:
        number_as_string = number_as_string[0]
    try:
        if len(number_as_string) > 1:
            int(str(number_as_string)[:-1])
        else:
            if len(number_as_string) == 0:
                raise ValueError
            if len(number_as_string) == 1 and number_as_string.isdigit():
                return int(number_as_string)
            else:
                raise ValueError
    except ValueError:
        raise ValueError
    last_char = str(number_as_string)[-1]
    if last_char.isdigit():
        return int(number_as_string)
    elif last_char == 'k':
        return int(number_as_string[:-1]) * 1000
    elif last_char == 'm':
        return int(number_as_string[:-1]) * 1000000
    elif last_char == 'b':
        return int(number_as_string[:-1]) * 1000000000
    else:
        raise ValueError


def format_as_table(content):
    # First line should be table headers
    # Each line after that should be the same length as content[0] and match
    # Every entry in content is a list of strings. If you send a non-string it will probably fail

    headers = content[0]
    # Figure out the length of each column based on the longest item in the column
    lens = [0] * len(headers)
    for i in range(0, len(headers)):
        for line in content:
            if len(line[i]) > lens[i]:
                lens[i] = len(line[i])

    out = "```"
    out += "\n"
    for i, header in enumerate(headers):
        out += header.center(lens[i]) + " |"

    out = out[:-2]
    out += "\n"

    for line in content[1:]:
        for i, field in enumerate(line):
            out += field.ljust(lens[i]) + " |"
        out = out[:-2]
        out += "\n"

    out += "```"
    print(out)
    return out


def format_adventure_line(*args):
    args_str = [str(arg) for arg in args]
    return ';'.join(args_str) + '\n'


def get_delta(finish_time):
    """Calculates the time remaining until a task is finished in minutes."""
    if type(finish_time) == str:  # File-based
        try:
            finish_time = datetime.datetime.strptime(finish_time, '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.datetime.now()
            delta = finish_time - current_time
            return math.floor(delta.total_seconds() / 60)
        except ValueError:
            raise ValueError

    # database based
    current_time = datetime.datetime.now(datetime.timezone.utc)
    delta = finish_time - current_time
    return math.floor(delta.total_seconds() / 60)


def calculate_finish_time(task_length):
    """Calculates the time when an adventure is over given its length."""
    return datetime.datetime.now() + datetime.timedelta(seconds=task_length)


def calculate_finish_time_utc(task_length):
    """Calculates the time (in UTC) when an adventure is over given its length."""
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=task_length)


def print_on_adventure_error(adventure):
    """Prints a string saying that the user cannot do two adventures at once."""
    out = f'Please finish that first before starting a new {adventure}.'
    return out


# truncate_task takes in a level to parse on and a number to make a judgement on. If the user has level 99, then
# truncate_task sends back the minimum of (1000, num_requested) as well as a boolean indicating it did The Thing.
# If user is < 99, then it does the same with 500 instead of 1000
def truncate_task(level: int, num: int) -> Tuple[int, bool]:
    if num > 1000:
        if level >= 99:
            return 1000, True

    if num > 500:
        if level < 99:
            return 500, True

    return num, False
