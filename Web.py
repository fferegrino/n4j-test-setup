import tornado.ioloop
import tornado.web
import time

from InsertAirports import InsertAirports
from InsertFlights import InsertFlights

# curl http://localhost:8888/other -d "location=~/Downloads/flight-delays/&instance=3.5.0-maps" -XGET
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        start_time = time.time()
        print("Inserting airports", start_time)
        insert = InsertAirports()
        instance = self.get_argument('instance')
        ti_maps_airlines, ti_maps, tr_maps = insert.insert(self.get_argument('location'), self.get_argument('instance'))
        end_time = time.time()
        time_elapsed = end_time - start_time
        print("Done inserting airports %f" % time_elapsed, end_time)
        self.write("other\t%s\t0\t%f\t%f\t%f\n" % (instance, ti_maps_airlines, ti_maps, tr_maps))

# curl http://localhost:8888/flights -d "location=~/Downloads/flight-delays/&instance=3.5.0-maps&flights=300" -XGET
class FlightsHandler(tornado.web.RequestHandler):
    def get(self):
        start_time = time.time()
        print("Inserting flights", start_time)
        insert = InsertFlights()
        instance = self.get_argument('instance')
        flights_no, ti_maps, tr_maps = insert.insert(self.get_argument('location'), int(self.get_argument('flights')), instance)
        end_time = time.time()
        time_elapsed = end_time - start_time
        print("Done inserting flights %f" % time_elapsed, end_time)
        self.write("flights\t%s\t%d\t%f\t%f\t0\n" % (instance, flights_no, ti_maps, tr_maps))

class LoadHandler(tornado.web.RequestHandler):
    def get(self):
        location = self.get_argument('location')
        InsertAirports.load_data(location)
        InsertFlights.load_data(location)
        self.write("Loaded\n")

def make_app():
    return tornado.web.Application([
        (r"/other", MainHandler),
        (r"/flights", FlightsHandler),
        (r"/load", LoadHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()