import sys
import time

start_time = time.time()
TARGET_TAG = "Live_In"

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)



if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
