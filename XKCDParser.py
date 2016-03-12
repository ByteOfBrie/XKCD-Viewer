'''
Drawille and curses xkcd reader
'''
import logging
from bs4 import BeautifulSoup
from drawille import Canvas
import requests
from io import BytesIO
from PIL import Image

class XKCDParser():
    '''
    the non-user interface parts of the xkcd viewer
    '''
    def __init__(self, comic_id=''):
        self.ids = [None, comic_id, None]
        self.title = None
        self.hover_text = None
        self.raw_img = None
        self.img = None
        self.parse_xkcd()

    def parse_xkcd(self):
        '''
        Gets all the data from the xkcd website, should probably be cleaned up a little
        '''
        url = 'http://xkcd.com/{}/'.format(self.ids[1])
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        comic_data = soup.find(id='comic').contents[1]
        img_url = 'http:' + str(comic_data.get('src'))
        logging.debug('loading %s', img_url)
        self.title = comic_data.get('alt')
        self.hover_text = comic_data.get('title')
        pic_data = requests.get(img_url)
        self.raw_img = Image.open(BytesIO(pic_data.content))
        logging.debug(self.raw_img)
        try:
            self.ids[0] = int(soup.find(rel='prev').get('href')[1:-1])
        except ValueError:
            pass
        try:
            self.ids[2] = soup.find(rel='next').get('href')[1:-1]
        except ValueError:
            pass
        self._make_canvas()
        logging.debug(self.img)

    def _make_canvas(self):
        '''
        use drawille functions to convert the image to text
        '''
        can = Canvas()
        img_bytes = self.raw_img.tobytes()
        place = [0, 0]

        for pix in img_bytes:
            if pix < 128:
                can.set(place[0], place[1])
            place[0] += 1
            if place[0] >= self.raw_img.size[0]:
                place[1] += 1
                place[0] = 0
        self.img = can.rows()
        logging.debug('row 0 len %s', len(can.rows()[0]))
        logging.debug('made canvas %s %s', len(self.img), len(max(self.img, key=len)))

    def next_comic(self):
        '''
        goes to the next comic if it exists
        '''
        if self.ids[2] is not None:
            self.ids[1] = self.ids[2]
            self.parse_xkcd()
        else:
            logging.info('no next comic found')

    def prev_comic(self):
        '''
        goes to the prev comic if it exists
        '''
        if self.ids[0] is not None:
            self.ids[1] = self.ids[0]
            self.parse_xkcd()
        else:
            logging.info('no prev comic found')

    def rand_comic(self):
        '''
        should parse xkcd's website for this
        '''
        self.ids[1] = requests.get('http://c.xkcd.com/random/comic/').url[16:-1]
        self.parse_xkcd()

    def set_id(self, comic_id):
        '''
        loads a given comic
        '''
        self.ids[1] = comic_id
        self.parse_xkcd()
