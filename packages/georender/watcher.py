import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


"""
credits to watchdog: https://pypi.org/project/watchdog/
helps to save the reloading time for each corresponding changes

"""
if __name__ == "__main__":    
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
    watcher_files = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, watcher_files, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
            