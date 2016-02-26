'''
The interactive part of the XKCD comic browser
'''

import sys
import curses
import logging
from XKCDParser import XKCDParser

PAD_MOVE_X = 5
PAD_MOVE_Y = 5

class XKCDViewer():
    '''
    basic control sof the image
    '''
    def __init__(self):
        self.parser = XKCDParser()

def main(stdscr):
    '''
    wrapped by curses
    '''
    logging.basicConfig(filename='xkcdviewer.log', level=logging.DEBUG)
    logging.info('starting program with screen size %s', str(stdscr.getmaxyx()))

    loading(stdscr)
    parser = XKCDParser()
    loaded = False
    while True:
        if not loaded:
            loaded = True
            messages = []
            pad_offset = [0, 0]

            pad, disp_dims = calculate_screen_dims(stdscr.getmaxyx(), messages, [''])
            lines = text_to_lines(parser.hover_text, disp_dims[1])
            pad, disp_dims = calculate_screen_dims(stdscr.getmaxyx(), messages, lines)

        stdscr.erase()
        img = parser.img
        img_dims = [len(img), len(max(img, key=len))]
        logging.debug('img_y, img_x %s', str(img_dims))
        logging.debug('disp_dims %s', str(disp_dims))

        vert = disp_dims[0] if disp_dims[0] < img_dims[0] else img_dims[0]
        for i in range(vert):
            j = disp_dims[1] if disp_dims[1] < img_dims[1] else img_dims[1]
            stdscr.addstr(i + pad[0], pad[2], img[i+pad_offset[0]][pad_offset[1] : pad_offset[1]+j])
        for i, line in enumerate(lines):
            stdscr.addstr(stdscr.getmaxyx()[0] - pad[1] + 1 + i, pad[2], line)
        stdscr.addstr(1, pad[2], 'Title:{}\t{}'.format(parser.title, parser.ids[1]))
        messages = list(item for item in messages if item)
        if messages:
            logging.debug(messages)
            for i, message in enumerate(messages):
                stdscr.addstr(2 + i, pad[2], message)
        cmd = stdscr.getkey()

        pad_offset, message, movement = parse_input(cmd, pad_offset, disp_dims, img_dims)
        if movement is None:
            messages = [message]
        elif movement == 1:
            loading(stdscr)
            parser.next_comic()
            loaded = False
        elif movement == 0:
            loading(stdscr)
            parser.rand_comic()
            loaded = False
        elif movement == -1:
            loading(stdscr)
            parser.prev_comic()
            loaded = False

def loading(stdscr):
    '''
    displays the loading message
    '''
    stdscr.erase()
    stdscr.addstr(stdscr.getmaxyx()[0]//2, stdscr.getmaxyx()[1]//2-5, 'loading...')
    stdscr.refresh()

def text_to_lines(hover_text, line_width):
    '''
    splits a string of words into lines of a given width
    '''
    hover_words = hover_text.split(' ')
    hover_lines = []
    line = ''
    for word in hover_words:
        if len(line) == 0:
            line += word
        elif len(line) + len(word) + 1 <= line_width:
            line += ' '
            line += word
        else:
            hover_lines.append(line)
            line = word
    hover_lines.append(line)
    return hover_lines

def calculate_screen_dims(screen_size, messages, lines):
    '''
    returns 2 tuples of the pad and the image width
    '''
    pad = [0, 0, 0, 0]
    disp_dims = [0, 0]
    pad[2] = 5
    pad[3] = 5
    disp_dims[1] = screen_size[1] - pad[2] - pad[3]
    pad[0] = 3 + len(messages) if messages else 4
    pad[1] = 2 + len(lines)
    disp_dims[0] = screen_size[0] - pad[0] - pad[1]
    return pad, disp_dims

def parse_input(cmd, pad_offset, disp_dims, img_dims):
    '''
    handle the input
    '''

    message = None

    if cmd == 'KEY_DOWN':
        pad_offset[0] += PAD_MOVE_Y
        if pad_offset[0] + disp_dims[0] >= img_dims[0]:
            message = 'Edge of image'
            pad_offset[0] = img_dims[0] - disp_dims[0] if img_dims[0] - disp_dims[0] > 0 else 0
    elif cmd == 'KEY_UP':
        pad_offset[0] -= PAD_MOVE_Y
        if pad_offset[0] <= 0:
            message = 'Edge of image'
            pad_offset[0] = 0
    elif cmd == 'KEY_RIGHT':
        pad_offset[1] += PAD_MOVE_X
        if pad_offset[1] + disp_dims[1] >= img_dims[1]:
            message = 'Edge of image'
            pad_offset[1] = img_dims[1] - disp_dims[1] if img_dims[1] - disp_dims[1] > 0 else 0
    elif cmd == 'KEY_LEFT':
        pad_offset[1] -= PAD_MOVE_X
        if pad_offset[1] <= 0:
            message = 'Edge of image'
            pad_offset[1] = 0
    elif cmd == 'z':
        return None, None, -1
    elif cmd == 'x':
        return None, None, 0
    elif cmd == 'c':
        return None, None, 1
    elif cmd == 'q':
        sys.exit(0)

    return pad_offset, message, None

if __name__ == '__main__':
    curses.wrapper(main)
