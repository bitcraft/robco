"""

"""
import contextlib
import curses
import yaml
import shlex
from inspect import signature

from . import simplefsm

with open('robco/strings.yaml') as fp:
    config = yaml.load(fp)
    options = config['options']
    strings = config['fo3']

buffer = ""


def client_out(text):
    global buffer
    buffer = text


def login(user=None):
    if user is None:
        client_out(strings['login_missing_name'])
        return

    users = options['users']
    passwd = ""
    if user in users and users[user]['pass'] == passwd:
        client_out(strings['login_pass'])
    else:
        client_out(strings['login_fail'])


def terminal(inquire=False):
    if inquire:
        client_out(strings['model_name'])
    else:
        client_out(strings['terminal_bad_options'])


def set():
    pass


def file(protection=None, inquire=False):
    if inquire:
        client_out('finq')


def halt():
    pass


def restart(maint=False):
    pass


def program_command(parent, func):
    sig = signature(func)
    cmd_options = sig.parameters
    cmd_name = func.__name__
    op_cmd = op_wait + cmd_name
    op_map[cmd_name] = func

    yield cmd_name, op_wait + parent, op_cmd
    if cmd_options:
        option_ctx = op_option + cmd_name
        for option_name, parameter in cmd_options.items():
            option_name = parameter.name
            store_ctx = op_store + option_name
            set_ctx = op_set + option_name

            yield option_token, op_cmd, option_ctx
            yield option_name, option_ctx, store_ctx

            yield set_token, store_ctx, set_ctx
            yield '*', set_ctx, 'fuck'


def program_parser(commands):
    events = [('reset', '*', op_wait)]

    for parent, cmd in commands:
        events.extend(program_command(parent, cmd))

    return simplefsm.SimpleFSM(events)


def parse(args):
    psm('reset')
    stack = list()
    tokenizer = shlex.shlex(args)
    tokenizer.wordchars += ":."

    for token in tokenizer:
        try:
            if options['case_insensitive']:
                psm(token.lower())
            else:
                psm(token)

        except simplefsm.TransitionError:
            op = psm.state[:3]

            if op == op_option:
                client_out(strings['bad_option'].format(token))

            elif stack:
                client_out(strings['bad_argument'].format(token))

            else:
                client_out(strings['syntax_error'].format(token))

            return

        op = psm.state[:3]
        if op == op_wait:
            stack.append([token, {}])

        elif op == op_store:
            stack[-1][1][token] = True

    return stack


def run_comands(instr):
    try:
        for name, kwargs in instr:
            if options['case_insensitive']:
                op_map[name.lower()](**{k.lower(): v for k, v in kwargs.items()})
            else:
                op_map[name.lower](**kwargs)
    except TypeError:  # arguments wrong for some reason
        client_out(strings['syntax_error'])


@contextlib.contextmanager
def curses_context():
    try:
        stdscr = curses.initscr()

        curses.cbreak()
        curses.noecho()
        stdscr.clear()
        stdscr.keypad(True)

        yield stdscr

    except Exception as e:
        client_out(e)

    finally:
        stdscr.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


# with curses_context() as c:
#     c.addstr(0, 0, 'fuck')
#     c.refresh()
#     time.sleep(2)

op_wait = '!w!'
op_option = '!o!'
op_store = '!s!'
op_set = '!t!'

set_state = 'set_state'

option_token = options['option_token']
set_token = options['set_token']
dict_token = options['dict_token']

terminal_values = {}
op_map = {}
psm = program_parser((
    ('', login),
    ('', set),
    ('set', terminal),
    ('set', file),
    ('set', halt),
    ('halt', restart),
))

# client_out('SET: OPTION [{}] NOT FOUND.'.format(name))
# client_out('SET: OPTION REQUIRED.')

for text, expected in strings['tests']:
    buffer = ""

    instr = parse(text.strip())
    if instr:
        run_comands(instr)

    if not expected == buffer:
        print("fail:", text)
        print(buffer)
        print()
