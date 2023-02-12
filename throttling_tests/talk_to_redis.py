import redis
import time

driver = redis.Redis(
    host = "localhost",
    port = 6379,
    socket_timeout = 0.1
)

t0 = time.time()
driver.zadd("set:INDEX", {"thread:1": 123456789})
t1 = time.time()
print(f"took {((t1-t0)*1000):.3f}ms to add element to sorted set.")

# Built in redis timeout isn't working! need to find a fix