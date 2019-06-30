import sys
import time

if __name__ == "__main__":
    start_time = time.time()
    print('cost time: {:.0f}:{:.2f}'.format((time.time()-start_time)/60,(time.time()-start_time)%60))