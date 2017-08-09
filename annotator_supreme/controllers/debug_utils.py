import time

class DebugUtils:

    start_time = None
    end_time = None
    @classmethod
    def tic(cls):
        cls.start_time = time.time()


    @classmethod
    def toc(cls, message = ""):
        elapsed = time.time() - cls.start_time
        print(message, str(elapsed*1000)+"ms")
        return elapsed
