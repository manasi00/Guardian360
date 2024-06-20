import os
import cv2
from scrfd import SCRFD, Threshold
from PIL import Image
import numpy as np
from detect_centroid_tracker import CentroidTracker
import uuid
import math
import sql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import sys

class ObjectDetection:
    def __init__(self, line_start, line_end, orientation='vertical', in_side='left', url=None):
        self.face_detector = SCRFD.from_path("./static/models/scrfd.onnx")
        self.threshold = Threshold(probability=0.4)
        self.line_start = line_start
        self.line_end = line_end
        self.orientation = orientation
        self.in_side = in_side
        self.face_count = 0
        self.human_count = 0
        self.id_direction = {}
        self.centroid_tracker = CentroidTracker()
        self.previous_positions = {}
        self.proximity_threshold = 20  # Threshold distance for proximity check
        self.url = url

    def detect_faces(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(frame)
        faces = self.face_detector.detect(pil_frame, threshold=self.threshold)
        return faces
    
    def save_face(self, face, raw_image, sav_path):
        bbox = face.bbox
        x1, y1, x2, y2 = int(bbox.upper_left.x), int(bbox.upper_left.y), int(bbox.lower_right.x), int(bbox.lower_right.y)
        face_image = raw_image[y1:y2, x1:x2]
        file_name = f"face_{uuid.uuid4()}.jpg"
        sav_path = os.path.join(sav_path, file_name)
        cv2.imwrite(sav_path, face_image)
        print(f"Saved {sav_path}")
        return file_name

    def line_counter(self, frame, faces, raw_image):
        in_sav_path = "./inference/static/face_image/in"
        out_sav_path = "./inference/static/face_image/out"
        
        if not os.path.exists(in_sav_path):
            os.makedirs(in_sav_path)
        if not os.path.exists(out_sav_path):
            os.makedirs(out_sav_path)
        
        rects = []
        for face in faces:
            bbox = face.bbox
            rects.append((bbox.upper_left.x, bbox.upper_left.y, bbox.lower_right.x, bbox.lower_right.y))
            cv2.rectangle(frame, (int(bbox.upper_left.x), int(bbox.upper_left.y)), (int(bbox.lower_right.x), int(bbox.lower_right.y)), (255, 0, 255), 1)

        # Update centroid tracker
        objects = self.centroid_tracker.update(rects)

        # Draw bounding boxes and centroids
        for (objectID, centroid) in objects.items():
            cv2.rectangle(frame, (int(centroid[0] - 10), int(centroid[1] - 10)), (int(centroid[0] + 10), int(centroid[1] + 10)), (255, 0, 255), 1)

            text = f"ID: {str(objectID)}"
            cv2.putText(frame, text, (int(centroid[0] - 10), int(centroid[1] - 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            if objectID in self.previous_positions:
                prev_centroid = self.previous_positions[objectID]

                if self.orientation == 'vertical':
                    if self.in_side == 'right':
                        if prev_centroid[0] < self.line_start[0] and centroid[0] >= self.line_start[0]:
                            self.id_direction[objectID] = 'in'
                            filename = self.save_face_for_object(objectID, faces, raw_image, in_sav_path)
                            if filename:
                                sql.face_in(filename)
                                self.send_email(os.path.join(in_sav_path, filename))
                                
                        elif prev_centroid[0] >= self.line_start[0] and centroid[0] < self.line_start[0]:
                            self.id_direction[objectID] = 'out'
                            self.save_face_for_object(objectID, faces, raw_image, out_sav_path)
                            
                    else:  # self.in_side == 'left'
                        if prev_centroid[0] > self.line_start[0] and centroid[0] <= self.line_start[0]:
                            self.id_direction[objectID] = 'in'
                            filename = self.save_face_for_object(objectID, faces, raw_image, in_sav_path)
                            if filename:
                                sql.face_in(filename)
                                self.send_email(os.path.join(in_sav_path, filename))
                                
                        elif prev_centroid[0] <= self.line_start[0] and centroid[0] > self.line_start[0]:
                            self.id_direction[objectID] = 'out'
                            self.save_face_for_object(objectID, faces, raw_image, out_sav_path)
                            
                elif self.orientation == 'horizontal':
                    if self.in_side == 'down':
                        if prev_centroid[1] < self.line_start[1] and centroid[1] >= self.line_start[1]:
                            self.id_direction[objectID] = 'in'
                            filename = self.save_face_for_object(objectID, faces, raw_image, in_sav_path)
                            if filename:
                                sql.face_in(filename)
                                self.send_email(os.path.join(in_sav_path, filename))
                                
                        elif prev_centroid[1] >= self.line_start[1] and centroid[1] < self.line_start[1]:
                            self.id_direction[objectID] = 'out'
                            self.save_face_for_object(objectID, faces, raw_image, out_sav_path)
                            
                    else:  # self.in_side == 'up'
                        if prev_centroid[1] > self.line_start[1] and centroid[1] <= self.line_start[1]:
                            self.id_direction[objectID] = 'in'
                            filename = self.save_face_for_object(objectID, faces, raw_image, in_sav_path)
                            if filename:
                                sql.face_in(filename)
                                self.send_email(os.path.join(in_sav_path, filename))
                                
                        elif prev_centroid[1] <= self.line_start[1] and centroid[1] > self.line_start[1]:
                            self.id_direction[objectID] = 'out'
                            self.save_face_for_object(objectID, faces, raw_image, out_sav_path)
                            
            else:
                self.id_direction[objectID] = None

            self.previous_positions[objectID] = centroid

        # Count in and out based on the ID direction
        count_in = sum(1 for direction in self.id_direction.values() if direction == 'in')
        count_out = sum(1 for direction in self.id_direction.values() if direction == 'out')

        # Display in and out counts
        cv2.line(frame, self.line_start, self.line_end, (0, 255, 0), 2)
        cv2.putText(frame, f'Count In: {count_in}', (15, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, bottomLeftOrigin=False)
        cv2.putText(frame, f'Count Out: {count_out}', (15, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, bottomLeftOrigin=False)

    def save_face_for_object(self, objectID, faces, raw_image, sav_path):
        if self.id_direction[objectID] in ['in', 'out']:
            for face in faces:
                # Check if the face corresponds to the objectID
                bbox = face.bbox
                x1, y1, x2, y2 = int(bbox.upper_left.x), int(bbox.upper_left.y), int(bbox.lower_right.x), int(bbox.lower_right.y)
                face_centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
                tracked_centroid = self.centroid_tracker.objects.get(objectID)
                if self.is_near(tracked_centroid, face_centroid):
                    return self.save_face(face, raw_image, sav_path)

    def is_near(self, tracked_centroid, face_centroid):
        # Calculate the Euclidean distance between the centroids
        distance = math.sqrt((tracked_centroid[0] - face_centroid[0]) ** 2 + (tracked_centroid[1] - face_centroid[1]) ** 2)
        return distance < self.proximity_threshold
    
    def send_email(self, image_path):
        # Email configuration
        sender_email = "guardian360.ahss@gmail.com"  # Your email
        receiver_email = "maanasee341@gmail.com"  # Receiver email
        password = "ijbw fhnt nxmt bdge"  # Your email password

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Person Detected Inside"

        # Add body to email
        body = "A person has been detected inside."
        message.attach(MIMEText(body, "plain"))

        # Add image attachment
        with open(image_path, "rb") as attachment:
            image_part = MIMEImage(attachment.read(), _subtype="jpg")
        image_part.add_header("Content-Disposition", "attachment", filename=os.path.basename(image_path))
        message.attach(image_part)

        # Log in to server using secure context and send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully")
    
    def __call__(self):
        capture = cv2.VideoCapture(self.url)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while True:
            ret, frame = capture.read()
            if not ret or frame is None:
                break

            # Flip the frame horizontally
            frame = cv2.flip(frame, 1)
            raw_frame = frame.copy()

            # Detect faces
            faces = self.detect_faces(frame)

            # Process the frame
            self.line_counter(frame, faces, raw_frame)

            # Display the frame
            # cv2.imshow("frame", raw_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        capture.release()
        cv2.destroyAllWindows()
        
        
def run(url):
    # Define the line start and end points
    line_start = (320, 0)
    line_end = (320, 480)
    orientation = 'vertical'
    in_side = 'right'

    # Initialize the ObjectDetection instance with the line counter
    detector = ObjectDetection(line_start=line_start, line_end=line_end, orientation=orientation, in_side=in_side, url=url)
    detector()
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
        run(url)
    else:
        print("Please provide a URL as an argument.")