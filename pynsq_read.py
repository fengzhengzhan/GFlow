import pickle
import time
import nsq
import threading
import tornado
start = time.time()

class Get_flow(object):
    def __init__(self, num):
        self.data = []
        self.num = num
        self.read_lock = threading.Lock()
        self.ioloop = tornado.ioloop.IOLoop.instance()

    def get_flow_func(self, number):
        def handler(message):
            try:
                if len(self.data) < number:
                    self.read_lock.acquire()
                    message.enable_async()
                    self.data.append(pickle.loads(message.body))
                    # print(str(message.body, encoding='utf-8'))
                    message.finish()
                    self.read_lock.release()
                else:
                    self.ioloop.add_callback(self.ioloop.stop)
                return True
            except Exception as e:
                # print(e)
                pass

        try:
            r = nsq.Reader(
                message_handler=handler,
                nsqd_tcp_addresses=['127.0.0.1:4150'],
                topic='flow',
                channel='read',
                max_in_flight=1)
            self.ioloop.start()
        except Exception as e:
            # print(e)
            pass

    def get_flow(self):
        try:
            self.data = []
            while True:
                if len(self.data) < self.num:
                    t = threading.Thread(target=self.get_flow_func, args=(self.num,))
                    t.start()
                    t.join()
                elif len(self.data) >= self.num:
                    self.data = self.data[:self.num]
                    break
            return self.data
        except Exception as e:
            # print(e)
            pass

if __name__ == "__main__":
    get_fl = Get_flow(10)
    for i in range(10):
        data = get_fl.get_flow()
        print(len(data), type(data), data)
        print()
