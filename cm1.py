from http import server
import threading
import time
import io
import picamera
import logging
import socketserver
from threading import Condition
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(27, GPIO.OUT) #trig alante
GPIO.setup(20, GPIO.OUT) #trig atras

GPIO.setup(4, GPIO.IN)  #echo alante
GPIO.setup(26, GPIO.IN) #echo atras

GPIO.setup(5, GPIO.OUT) #alante
alante = GPIO.PWM(5,100)

GPIO.setup(6, GPIO.OUT) #atras
atras = GPIO.PWM(6,100)

alante.start(80)

time.sleep(0.2)
alante.ChangeDutyCycle(30)


def camara():
	from http import server
#29
	PAGE="""\
	<html>
	<head>
	<title>Raspberry Pi - Camera</title>
	</head>
	<body>
	<center><h1>Raspberry Pi - Camera</h1></center>
	<center><img src="stream.mjpg" width="640" height="480"></center>
	</body>
	</html>
	"""
	class StreamingOutput(object):
	   	def __init__(self):
	        	self.frame = None
	        	self.buffer = io.BytesIO()
	        	self.condition = Condition()

	   	def write(self, buf):
	        	if buf.startswith(b'\xff\xd8'):
	            		self.buffer.truncate()
	            		with self.condition:
	              			self.frame = self.buffer.getvalue()
	              			self.condition.notify_all()
	              			self.buffer.seek(0)
	            		return self.buffer.write(buf)
#55
	class StreamingHandler(server.BaseHTTPRequestHandler):
	    	def do_GET(self):
	        	if self.path == '/':
	           		self.send_response(301)
	           		self.send_header('Location', '/index.html')
	           		self.end_headers()
	        	elif self.path == '/index.html':
	           		content = PAGE.encode('utf-8')
	           		self.send_response(200)
	           		self.send_header('Content-Type', 'text/html')
	           		self.send_header('Content-Length', len(content))
	           		self.end_headers()
	           		self.wfile.write(content)
	        	elif self.path == '/stream.mjpg':
	            		self.send_response(200)
	            		self.send_header('Age', 0)
	            		self.send_header('Cache-Control', 'no-cache, private')
	            		self.send_header('Pragma', 'no-cache')
	            		self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
	            		self.end_headers()

#76
	            		try:
	                		while True:
	                    			with output.condition:
	                        			output.condition.wait()
	                        			frame = output.frame
	                    			self.wfile.write(b'--FRAME\r\n')
	                    			self.send_header('Content-Type', 'image/jpeg')
	                    			self.send_header('Content-Length', len(frame))
	                    			self.end_headers()
	                    			self.wfile.write(frame)
	                    			self.wfile.write(b'\r\n')
	            		except Exception as e:
	                		logging.warning(
#90

	                    		'Removed streaming client %s: %s',
	                    		self.client_address, str(e))
	        	else:
	            		self.send_error(404)
	            		self.end_headers()

	class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
	  	allow_reuse_address = True
	  	daemon_threads = True

	with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
	  	output = StreamingOutput()
#Uncomment the next line to change your Pi's Camera rotation (in degrees)
	  	camera.rotation = 180
	  	camera.start_recording(output, format='mjpeg')
	try:
	  	address = ('', 8000)
	  	server = StreamingServer(address, StreamingHandler)
	  	server.serve_forever()
	except:
		print("error")

	finally:
	  	camera.stop_recording()




def sensor():
	try:
		while True:

	                start = 0
	                end = 0
	                GPIO.output(27, False)
#122
	                time.sleep(0.2)
	                GPIO.output(27, True)

	                time.sleep(10*10**-6)
	                GPIO.output(27, False)

	                while GPIO.input(4) == GPIO.LOW:

	                        start = time.time()
#132

	                while GPIO.input(4) == GPIO.HIGH:

	                        end = time.time()

	                distancia = (end-start) * 340 / 2

	                print("Distancia al objeto1 =", str(distancia))

	                if distancia < 0.22:

	                        alante.stop()
	                        print("Distancia = 2", str(distancia))

	                        atras.start(100)
	                        time.sleep(0.2)
	                        atras.stop()
	                        print("primer cleanup")
                        #GPIO.setmode(GPIO.BCM)
                        #GPIO.setup(6, GPIO.OUT) #atras
                        #atras = GPIO.PWM(6,100)
	                        print("estoy delante del segundo cleanup")
                        #GPIO.output(6, 0)
                        #GPIO.cleanup()
	                        print("segundo cleanup")

	                        break

	except:
		print("error")
		GPIO.cleanup()

hilo1 = threading.Thread(target=camara)
hilo2 = threading.Thread(target=sensor)

hilo1.start()
hilo2.start()

