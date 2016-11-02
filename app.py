from tornado import websocket, web, ioloop
import json
import base64
import zbar
from PIL import Image
import urllib, cStringIO

cl = []

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_message(self, msg):
        #print msg
        if msg.find('base64') != -1:
            if msg.find('png') != -1:
                frm = "png"
            elif msg.find('jpg') != -1:
                frm = "png"
            elif msg.find('gif') != -1:
                frm = "gif"
            out = self.barcode(msg)
            print "Decoded: Type ",out[0]," Data ",out[1]
            jn = {"type": str(out[0]),"value":out[1]}
            self.write_message(json.dumps(jn))


    def on_close(self):
        if self in cl:
            cl.remove(self)

    def barcode(self, msg):

        file = cStringIO.StringIO(urllib.urlopen(msg).read())
        # create a reader
        scanner = zbar.ImageScanner()

        # configure the reader
        scanner.parse_config('enable')

        # obtain image data
        pil = Image.open(file).convert('L')
        width, height = pil.size
        raw = pil.tobytes()
        #pil.show()
        # wrap image data
        image = zbar.Image(width, height, 'Y800', raw)

        # scan the image for barcodes
        scanner.scan(image)

        # extract results
        for symbol in image:
            # do something useful with results
            print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
        # clean up
        del(image)

        return symbol.type, symbol.data

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value" : value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        pass

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './'}),
])


if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()
