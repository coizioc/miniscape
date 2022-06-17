import datetime
import logging
import random

from config import ADVENTURES_FILE
from errors import AdventureNotFoundError
from miniscape import slayer_helpers as sh, clue_helpers, quest_helpers, craft_helpers

# An adventure in the adventure file is stored as the following (with semicolon delimiters in between):
# adventureid, userid, completion_time, guildid, channelid, *args
# where *args represent adventure-specific arguments.
from miniscape.models import Task
from utils.command_helpers import get_delta


def get_adventure(userid):
    userid = str(userid)
    for line in get_list():
        if userid in line:
            return line.split(';')

    tasks = Task.objects.filter(user__id=userid)
    if len(tasks) == 0:
        raise AdventureNotFoundError
    return tasks.first()



def get_finished():
    """Gets a list of adventures with time preceding the current time, removes those from the adventure file,
    and returns the list of finished adventures."""
    adventures = get_list()
    finished_adventures = []
    current_time = datetime.datetime.now()
    out = ''
    for adventure in adventures:
        # Sometimes there's an empty new line at the beginning of the file. It's weird
        if not adventure:
            continue
        adventure_args = adventure.split(';')
        time = adventure_args[2]
        finish_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        if finish_time < current_time:
            finished_adventures.append(adventure_args)
        else:
            out += f'{adventure}\n'
    write(out, overwrite=True)
    return finished_adventures


def get_list():
    """Opens the adventures file and returns a list of adventures."""
    with open(ADVENTURES_FILE, 'r') as f:
        lines = f.read().splitlines()
    return lines


def is_on_adventure(userid):
    """Determines whether a user is already on/is preparing for an adventure."""
    userid = str(userid)
    for adventure in get_list():
        if userid in adventure:
            return True

    tasks = Task.objects.filter(user__id=userid)
    if len(tasks) == 0:
        return False
    return True


def is_success(chance):
    """Determines whether an adventure is successful or not."""
    if random.randint(0, 100) <= int(chance):
        return True
    else:
        return False


def print_adventure(userid):
    userid = str(userid)
    for line in get_list():
        if userid in line:
            adventure = line.split(';')
            break
    else:
        try:
            tasks = Task.objects.filter(user__id=userid)
            adventure = tasks[0]
            if len(tasks) == 0:
                raise KeyError
        except Exception as e:
            logging.getLogger(__name__).error("error encountered checking db for tasks: %s", str(e))
            raise KeyError

    if type(adventure) == list:
        adventureid, userid, finish_time = adventure[0:3]
        adventures = {
            '0': sh.print_status,
            '1': sh.print_kill_status,
            '2': quest_helpers.print_status,
            '3': craft_helpers.print_status,
            '4': clue_helpers.print_status,
            '5': sh.print_reaper_status,
            '6': craft_helpers.print_rc_status
        }
        time_left = get_delta(finish_time)
        if time_left == 1:
            time_string = 'in 1 minute'
        elif time_left < 1:
            time_string = 'soon'
        else:
            time_string = f'in {time_left} minutes'
        out = adventures[adventureid](userid, time_string, adventure[5:])
        return out
    else:
        adventures = {
            "runecraft": craft_helpers.print_rc_status2
        }
        time_left = get_delta(adventure.completion_time)
        ret = adventures[adventure.type](adventure, time_left)
        return ret


def read(userid):
    """Finds an adventure from a userid and returns the values of the adventure as a list."""
    userid = str(userid)
    adventures = get_list()

    for adventure in adventures:
        if userid in adventure:
            return adventure.split(';')
    else:
        raise ValueError


def remove(userid):
    """Removes an adventure from the adventures file containing the userid."""
    userid = str(userid)
    new_adventures = [adventure for adventure in get_list() if userid not in adventure]
    write('\n'.join(new_adventures) + '\n', overwrite=True)


def write(data, overwrite=False):
    """Writes/Appends a string representing adventures to the adventure file."""
    operation = 'w+' if overwrite else 'a+'

    with open(ADVENTURES_FILE, operation) as f:
        f.write(data)
