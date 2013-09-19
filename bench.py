'''A quick-and-dirty benchmark'''

import time
import string
from nback import Nback

nback = Nback(3, 3, 5, {1: 2, 2: 4})
count = 1000

start = - time.time()
results = [nback.sequence(string.lowercase) for _ in range(count)]
start += time.time()
print '%s sequences in %fs (%10.2f sequences / second)' % (
    count, start, count / start)
