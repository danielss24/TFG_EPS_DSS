import time

while True:
    try:
        time.sleep(3)
        print ("Zzzz")
        time.sleep(3)
        print("gong!")
    except KeyboardInterrupt as e:
        print ("Closed by an Interrupt")
        break