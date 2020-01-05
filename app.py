import os
import random
import string
import cherrypy
import redis
import json
from scrap import scrap

# db = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)
db = redis.from_url(os.environ.get("REDIS_URL"))


class WebService(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def data(self):
        l = list(db.smembers("data"))
        for i in range(len(l)):
            l[i] = json.loads(l[i])

        return json.dumps(l)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def update(self):
        count = scrap()
        if count:
            dic = {
                "status": 1,
                "message": "{} stock records fetched and updated.".format(count),
            }
        else:
            dic = {
                "status": 0,
                "message": "Failed to update stock data",
            }
        return json.dumps(dic)
        
    @cherrypy.expose
    def index(self):
        return open("./index.html", "r").read()


if __name__ == "__main__":
    conf = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': int(os.environ.get('PORT', 5000)),
        },
        '/': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*')],
        }
    }
    cherrypy.quickstart(WebService(), '/', conf)