from threading import Thread
from knowemployee import app, run_analytics

if __name__ == '__main__':
    Thread(target=run_analytics).start()
    app.run()