import math
import time


class StepTimer():
    def __init__(self, step):
        self.step = step
        
    
    def __enter__(self):
        self.start = time.time()
        
    def __exit__(self, type, value, traceback):
        stop = time.time()
        
        mins = math.floor((stop - self.start) / 60)
        secs = round((stop - mins * 60) % 60, 2)
        
        print(f'Finished step: {self.step}\nTime elapsed: {mins} minutes and {secs} seconds.\n')