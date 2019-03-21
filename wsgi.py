# -*- coding: utf-8 -*-

#from werkzeug.serving import run_simple
#from werkzeug.wsgi import DispatcherMiddleware

#from app import app

#application = DispatcherMiddleware(app)

#if __name__ == "__main__":
#    run_simple(
#        '0.0.0.0',
#        80,
#        application,
#        use_reloader=True,
#       use_debugger=True
#    )

from cheroot import wsgi
from app import app

server = wsgi.Server(('0.0.0.0', 80), app)

if __name__ == '__main__': 
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
