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
    def __init__(self, stdscr, parser):
        self.parser = parser
        self.messages = []
        self.text = ['', ['']]
        self.stdscr = stdscr
        self.pad = [0, 0, 0, 0]
        self.pad_offest = [0, 0]
        self.disp_dims = [0, 0]
        self.lines = ['']

    def loading(self):
        '''
        displays the loading message
        '''
        self.stdscr.erase()
        self.stdscr.addstr(self.stdscr.getmaxyx()[0]//2,
                           self.stdscr.getmaxyx()[1]//2-5, 'loading...')
        self.stdscr.refresh()

    def set_up_padding(self):
        '''
        creates the pads for the screen
        '''
        self.calculate_screen_dims(self.stdscr.getmaxyx(), self.messages, self.text[1])
        self._text_to_lines()
        self.calculate_screen_dims(self.stdscr.getmaxyx(), self.messages, self.text[1])

    def set_up_for_viewing(self):
        '''
        runs the basic functions
        '''

        self.text[0] = self._text_to_lines()


    def _text_to_lines(self):
        '''
        splits a string of words into lines of a given width
        '''
        line_width = self.valid_disp_dims[1]
        hover_words = self.parser.hover_text.split(' ')
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
        self.text[1] = hover_lines

    def calculate_screen_dims(self, screen_size, messages, lines):
        '''
        returns 2 tuples, pad and image dimensions
        '''
        pad = [0, 0, 0, 0]
        valid_disp_dims = [0, 0]
        disp_dims = [0, 0]
        pad[2] = 5
        pad[3] = 5
        valid_disp_dims[1] = screen_size[1] - pad[2] - pad[3]
        pad[0] = 3 + len(messages) if messages else 4
        pad[1] = 2 + len(lines)
        valid_disp_dims[0] = screen_size[0] - pad[0] - pad[1]
        img_dims = [len(self.img), len(max(self.img, key=len))]
        disp_dims[0] = min(valid_disp_dims[0], img_dims[0])
        disp_dims[1] = min(valid_disp_dims[1], img_dims[1])
        self.valid_disp_dims = valid_disp_dims
        self.pad = pad
        self.disp_dims = disp_dims
        return pad, disp_dims



def main(stdscr):
    '''
    wrapped by curses
    '''
    logging.basicConfig(filename='xkcdviewer.log', level=logging.DEBUG)
    logging.info('starting program with screen size %s', str(stdscr.getmaxyx()))


    parser = XKCDParser()
    viewer = XKCDViewer(stdscr, parser)
    viewer.loading()

    loaded = False
    while True:
        viewer.set_up_padding()

        stdscr.erase()
        img = parser.img
        img_dims = [len(img), len(max(img, key=len))]
        logging.debug('disp_dims %s', str(viewer.disp_dims))
    
        #height of image displayed, min of image height and screen height
        for i in range(viewer.disp_dims[0]):   #new disp_dims
            #width of image, min of image width and screen width
            stdscr.addstr(i + pad[0], pad[2],
                          img[i+pad_offset[0]][pad_offset[1] : pad_offset[1]+viewer.disp_dims[1]])

        #output hover text/title
        for i, line in enumerate(lines):
            stdscr.addstr(stdscr.getmaxyx()[0] - pad[1] + 1 + i, pad[2], line)
        stdscr.addstr(1, pad[2], 'Title:{}\t{}'.format(parser.title, parser.ids[1]))

        #errors or other messages
        messages = list(item for item in messages if item)
        if messages:
            logging.debug(messages)
            for i, message in enumerate(messages):
                stdscr.addstr(2 + i, pad[2], message)
        cmd = stdscr.getkey()
    
        #taking input
        pad_offset, message, movement = parse_input(cmd, pad_offset, viewer.valid_disp_dims, img_dims)
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
