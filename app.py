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
        #check for base64 encode
        if msg.find('base64') != -1:
            #pass DataURI to barcode function
            out = self.barcode(msg)
            #check for return data type
            if type(out).__name__ == "tuple":
                print "Decoded: Type ",out[0]," Data ",out[1]
                jn = {"type": str(out[0]),"value":out[1]}
                self.write_message(json.dumps(jn))
            else:
                print out
                self.write_message(str(out))

    def on_close(self):
        if self in cl:
            cl.remove(self)

    def barcode(self, msg):
        #read DataURI as file
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
        istrue = scanner.scan(image)
        if istrue == 1:
        # extract results
            for symbol in image:
                # do something useful with results
                print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
            # clean up
            del(image)

            return symbol.type, symbol.data
        else:
            return "Unrecognised Image : Sytem couldn't detect clear Barcode in the image selected"


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
])


if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()
