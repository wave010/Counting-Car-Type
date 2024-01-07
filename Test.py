import cv2
from datetime import datetime, timedelta

cap = cv2.VideoCapture(0)

# Set the initial time
start_time = datetime.now()

# Set the time interval for printing "Hello" (1 minutes in this case)
time_interval = timedelta(minutes=1)

# Set the total duration for the program (2 minutes in this case)
total_duration = timedelta(minutes=2)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Check if it's time to print "Hello"
    current_time = datetime.now()
    elapsed_time = current_time - start_time

    if elapsed_time >= time_interval:
        print("Hello")
        # Update the start time for the next interval
        start_time = current_time

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Our operations on the frame come here
    frame = cv2.resize(frame, (640, 360))

    if elapsed_time >= total_duration:
        print("Program ending after 2 minutes.")
        break
    # Display the resulting frame
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
