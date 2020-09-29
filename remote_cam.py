import cv2
import paho.mqtt.client as mqtt
import base64
import ssl


faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
video_capture = cv2.VideoCapture(0, cv2.CAP_V4L)

## MQTT
MQTT_PORT = 8883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "cam"
MQTT_HOST = "a32h7qznr08z7a-ats.iot.us-east-1.amazonaws.com"
CA_ROOT_CERT_FILE = "/etc/mosquitto/certs/rootCA.pem"
THING_CERT_FILE = "/etc/mosquitto/certs/cert.crt"
THING_PRIVATE_KEY = "/etc/mosquitto/certs/private.key"


# Define on_publish event function
def on_publish(client, userdata, mid):
        print ("Message Published...")

my_client = mqtt.Client()
my_client.on_publish = on_publish

# Configure TLS Set
my_client.tls_set(CA_ROOT_CERT_FILE, certfile=THING_CERT_FILE, keyfile=THING_PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

# Connect with MQTT Broker
my_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
my_client.loop_start()

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    if len(faces) > 0:
        print ("Found face")
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        _, buffer = cv2.imencode('.jpg', frame)
        raw_data = base64.b64encode(buffer)
        my_client.publish(MQTT_TOPIC, raw_data)
    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
my_client.disconnect()

