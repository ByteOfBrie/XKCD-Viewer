'''
The interactive part of the XKCD comic browser
'''

import sys
import curses
import logging
from XKCDParser import XKCDParser

PAD_MOVE_X = 5
PAD_MOVE_Y = 5

UP = ('KEY_UP')
DOWN = ('KEY_DOWN')
LEFT = ('KEY_LEFT')
RIGHT = ('KEY_RIGHT')
PREV = ('z')
RAND = ('x')
NEXT = ('c')
EXIT = ('q')
CUSTOM = ('/')

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
        self.pad_offset = [0, 0]
        self.disp_dims = [0, 0]
        self.lines = ['']
        self.img = None

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

    def reset_img(self):
        self.img = self.parser.img
        self.img_dims = [len(self.img), len(max(self.img, key=len))]

        self.pad_offset = [0, 0]        

    def calculate_screen_dims(self, screen_size, messages, lines):
        '''
        returns 2 tuples, pad and image dimensions
        '''
        
        if self.img is None:
            self.reset_img()

        pad = [0, 0, 0, 0]
        valid_disp_dims = [0, 0]
        disp_dims = [0, 0]
        img_dims = self.img_dims


        pad[2] = 5
        pad[3] = 5
        valid_disp_dims[1] = screen_size[1] - pad[2] - pad[3]
        pad[0] = 3 + len(messages) if messages else 4
        pad[1] = 2 + len(lines)
        valid_disp_dims[0] = screen_size[0] - pad[0] - pad[1]
        disp_dims[0] = min(valid_disp_dims[0], img_dims[0])
        disp_dims[1] = min(valid_disp_dims[1], img_dims[1])
        self.valid_disp_dims = valid_disp_dims
        self.pad = pad
        self.disp_dims = disp_dims
        return pad, disp_dims

    def parse_input(self):
        cmd = self.stdscr.getkey()
        
        self.messages = []

        if cmd in DOWN:
            self.pad_offset[0] += PAD_MOVE_Y
            if self.pad_offset[0] + self.disp_dims[0] >= self.img_dims[0]:
                self.messages.append('Edge of image')
                self.pad_offset[0] = max(self.img_dims[0] - self.disp_dims[0], 0)
        elif cmd in UP:
            self.pad_offset[0] -= PAD_MOVE_Y
            if self.pad_offset[0] <= 0:
                self.messages.append('Edge of image')
                self.pad_offset[0] = 0
        elif cmd in RIGHT:
            self.pad_offset[1] += PAD_MOVE_X
            if self.pad_offset[1] + self.disp_dims[1] >= self.img_dims[1]:
                self.messages.append('Edge of image')
                self.pad_offset[1] = max(self.img_dims[1] - self.disp_dims[1], 0)
        elif cmd in LEFT:
            self.pad_offset[1] -= PAD_MOVE_X
            if self.pad_offset[1] <= 0:
                self.messages.append('Edge of image')
                self.pad_offset[1] = 0
        elif cmd in PREV:
            self.loading()
            self.parser.prev_comic()
            self.reset_img()
        elif cmd in RAND:
            self.loading()
            self.parser.rand_comic()
            self.reset_img()
        elif cmd in NEXT:
            self.loading()
            self.parser.next_comic()
            self.reset_img()
        elif cmd in CUSTOM:
            #this is going to be terrible
            comic_id = ''
            for _ in range(10):
                cmd = self.stdscr.getch()
                logging.debug(cmd)
                if cmd == 27:
                    logging.debug('esc pressed')
                    break

                #number input - no support for numpad
                elif cmd >= 48 and cmd <= 57:
                    comic_id += str(cmd - 48)
                
                elif cmd == 10:     #enter
                    logging.debug(comic_id)
                    self.loading()
                    self.parser.set_id(int(comic_id))
                    self.reset_img()

                elif cmd == 127:    #backspace
                    if len(comic_id) > 0:
                        comic_id = comic_id[:-1]

                #a terrible solution is still a solution
                self.stdscr.addstr(0, self.pad[2], 'ID:              ')
                self.stdscr.addstr(0, self.pad[2], 'ID:{}'.format(comic_id))

        elif cmd in EXIT:
            sys.exit(0)

def main(stdscr):
    '''
    wrapped by curses
    '''
    logging.basicConfig(filename='xkcdviewer.log', level=logging.DEBUG)
    logging.info('starting program with screen size %s', str(stdscr.getmaxyx()))


    parser = XKCDParser()
    viewer = XKCDViewer(stdscr, parser)
    viewer.loading()

    while True:
        viewer.set_up_padding()

        stdscr.erase()
        img = parser.img
        logging.debug('disp_dims %s', str(viewer.disp_dims))
    
        #height of image displayed, min of image height and screen height
        for i in range(viewer.disp_dims[0]):
            #width of image, min of image width and screen width
            stdscr.addstr(i + viewer.pad[0], viewer.pad[2],
                          img[i+viewer.pad_offset[0]][viewer.pad_offset[1] :
                          viewer.pad_offset[1]+viewer.disp_dims[1]])

        #output hover text/title
        for i, line in enumerate(viewer.lines):
            stdscr.addstr(stdscr.getmaxyx()[0] - viewer.pad[1] + 1 + i, viewer.pad[2], line)
        stdscr.addstr(1, viewer.pad[2], 'Title:{}\t{}'.format(parser.title, parser.ids[1]))

        #errors or other messages
        messages = list(item for item in viewer.messages if item)
        if messages:
            logging.debug(messages)
            for i, message in enumerate(messages):
                stdscr.addstr(2 + i, viewer.pad[2], message)
        
        
        #taking input
        viewer.parse_input()

if __name__ == '__main__':
    curses.wrapper(main)
