# Harvey Randall 09/11/2021, for the Rocket Program

# Global Imports
from picamera import PiCamera
import time
from datetime import datetime
from sense_hat import SenseHat
import threading
import shlex
import subprocess

#Global Variables
running = False # Variable to stop the camera recording
filename = "Harveys_Mission_To_Mars_"+datetime.now().strftime("%d_%m_%y_%H_%M_%S") # Set the filename
now = datetime.now() # Get the current time
camera = PiCamera() # Initialise the camera
sense = SenseHat() # Initialise the sense hat
sense.clear() # Clear the matrix

# Set Camera up
camera.resolution = (1920, 1080)

# Default values
o = sense.get_orientation()

# Starting camera annotations
camera.annotate_text = now.strftime("%d/%m/%y %H:%M:%S Hum:{f} Temp:{t} Acc:{a} Yaw:{yaw} Pitch:{pitch} Roll:{roll}".format(f=round(sense.get_humidity(),1), t=round(sense.get_temperature(),1), a=round(sense.get_accelerometer_raw()['y'],1), y=round(sense.get_orientation_radians()['yaw'],1), pitch=round(o['pitch'],1), yaw=round(o['yaw'],1), roll=round(o['roll'],1)))

# CSV Headers
arrayOut = ["timestamp\tHumidity\tTemperature\tAccelleration\tYaw\tPitch\tRoll\n"]

# Async function to update camera annotation
def runCamera(stop):
    # First start recording
    camera.start_recording(filename+'.h264')
    running = True

    # Now loop while the code is running
    while running == True:
        # Sample rate of 10hz
        time.sleep(0.1)

        # Some local scoped variables
        now = datetime.now()
        o = sense.get_orientation()

        # Add Camera Annotations
        camera.annotate_text = now.strftime("%d/%m/%y %H:%M:%S Hum:{f} Temp:{t} Acc:{a} Yaw:{yaw} Pitch:{pitch} Roll:{roll}".format(f=round(sense.get_humidity(),1), t=round(sense.get_temperature(),1), a=round(sense.get_accelerometer_raw()['x'],1), y=round(sense.get_orientation_radians()['yaw'],1), pitch=round(o['pitch'],1), yaw=round(o['yaw'],1), roll=round(o['roll'],1)))
        
        # CSV add line to array
        arrayOut.append(now.strftime("%d/%m/%y %H:%M:%S\t{f}\t{t}\t{a}\t{yaw}\t{pitch}\t{roll}\n".format(f=round(sense.get_humidity(),1), t=round(sense.get_temperature(),1), a=round(sense.get_accelerometer_raw()['x'],1), y=round(sense.get_orientation_radians()['yaw'],1), pitch=round(o['pitch'],1), yaw=round(o['yaw'],1), roll=round(o['roll'],1))))
        
        # If the stop flag is called stop loop
        if stop():
                break


# Start Async func
stop_threads = False
# Declare thread
thread1 = threading.Thread(target=runCamera, args =(lambda : stop_threads, ))
thread1.start()

# Wait 10 minutes
time.sleep(60 * 10)

# Stop threads and recording so we can proccess the data
stop_threads = True
running = False
camera.stop_recording()

# Convert the h264 video to mp4 so it is easily readable for the end user
command = shlex.split("MP4Box -add {f}.h264 {f}.mp4".format(f=filename))
output = subprocess.check_output(command, stderr=subprocess.STDOUT)

# Super simple write csv to file system, making sure to close it
f = open(filename+".csv", "w")
f.write(' '.join(arrayOut))
f.close()

# Debuggin make sure the file converted
print(output)

# Prepare the matrix to the end user that they can safely unplug the Pi
r = 255
g = 0
b = 0
# done alert
sense.clear((r, g, b))

# END OF PROGRAM