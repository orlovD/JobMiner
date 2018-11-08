import sched, time
from threading import Timer
from datetime import datetime
import getPostsFromGroups

TIME_INTERVAL = 60*60*24 #one day

def print_time(): 
	print datetime.now()


def main():
	while True:
		Timer(TIME_INTERVAL, getPostsFromGroups.startUpdate, ()).start()
		Timer(TIME_INTERVAL, print_time,()).start()
		time.sleep(TIME_INTERVAL)  # sleep while time-delay events execute

if __name__ == "__main__":
    main()
