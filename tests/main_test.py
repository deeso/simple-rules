import unittest
import os
import signal

if __name__ == '__main__':

    unittest.main()
    os.kill(os.getpid(), signal.SIGKILL)
