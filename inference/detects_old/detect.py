import torch
import numpy as np
import cv2
import datetime as dt
from time import time
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from detect_centroid_tracker import CentroidTracker
from pathlib import Path
import os
import sqlite3
import sql
import uuid  # Import the uuid module to generate unique identifiers
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class ObjectDetection:
    def __init__(self, capture_index, line_start, line_end):
        self.capture_index = capture_index

        # Model information
        self.model = YOLO("./inference/Model/best.pt")

        # Visual information
        self.annotator = None
        self.start_time = 0
        self.end_time = 0

        # Dict mapping class_id to class_name
        self.CLASS_NAMES_DICT = self.model.model.names

        # Class_ids of interest - face and human
        self.selected_classes = [0, 1]

        # Device information
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Line counter information
        self.line_start = line_start
        self.line_end = line_end
        self.face_count = 0
        self.human_count = 0

        # Previous frame's class IDs
        self.prev_class_ids = []

        # Centroid tracker
        self.centroid_tracker = CentroidTracker()

        # Dictionary to store IDs and their crossing direction
        self.id_direction = {}

        # Dictionary to map object IDs to unique identifiers
        self.id_to_unique_id = {}

    def predict(self, im0):
        # Run prediction using a YOLO model for the input image `im0`.
        results = self.model(im0)
        return results

    def display_fps(self, im0):
        # Displays the FPS on an image `im0` by calculating and overlaying as white text on a black rectangle
        self.end_time = time()
        fps = 1 / np.round(self.end_time - self.start_time, 2)
        text = f'FPS: {int(fps)}'
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        gap = 10
        cv2.rectangle(im0, (20 - gap, 70 - text_size[1] - gap), (20 + text_size[0] + gap, 70 + gap), (255, 255, 255), -1)
        cv2.putText(im0, text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    def plot_bboxes(self, results, im0):
        # Plots bounding boxes on an image given detection results; returns annotated image and class IDs.
        class_ids = []
        self.annotator = Annotator(im0, 3, results[0].names)
        boxes = results[0].boxes.xyxy.cpu()
        clss = results[0].boxes.cls.cpu().tolist()
        names = results[0].names
        for box, cls in zip(boxes, clss):
            #  Class 'face'
            class_ids.append(cls)
            if cls == 0:
                self.annotator.box_label(box, label=names[int(cls)], color=colors(int(cls), True))
        return im0, class_ids

    def line_counter(self, im0, class_ids, results, raw_image):
        # Counts occurrences of 'face' and 'human' classes when crossing the line.
        rects = []
        for i, cls in enumerate(class_ids):
            if cls == 0:  # Class 'face'
                box = results[0].boxes.xyxy.cpu()[i]
                startX, startY, endX, endY = box[0], box[1], box[2], box[3]
                rects.append((startX, startY, endX, endY))
                self.face_count += 1
            elif cls == 1:  # Class 'human'
                self.human_count += 1

        # Update centroid tracker
        objects = self.centroid_tracker.update(rects)

        # Draw centroid tracking results
        for (objectID, centroid) in objects.items():
            text = f"ID {objectID}"
            cv2.putText(im0, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(im0, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            
            # Check if the object has crossed the line                
            if centroid[0] < self.line_start[0]:
                self.id_direction[objectID] = 'in'
                if objectID not in self.id_to_unique_id:
                    sql.create_table()
                    base_filename = 'face_image'
                    image_sav_path = Path('./inference/face_image/enter/')
                    
                    if not os.path.exists(image_sav_path):
                        os.makedirs(image_sav_path)
                    
                    # Generate a unique identifier for the person
                    if objectID not in self.id_to_unique_id:
                        unique_id = str(uuid.uuid4())[:8]  # Generate a random UUID and take the first 8 characters
                        self.id_to_unique_id[objectID] = unique_id
                    
                    # Save the image with the unique identifier
                    imag_filename = os.path.join(image_sav_path, f"{base_filename}_{self.id_to_unique_id[objectID]}.jpg")
                    cv2.imwrite(imag_filename, raw_image)
                    
                    conn = sqlite3.connect("./db.sqlite3")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Events (face_path, entered_at, exited_at) VALUES (?,?,?)", (imag_filename, dt.datetime.now(), None))
                    try:
                        conn.commit()
                        print('Data added to database')
                    except sqlite3.Error as e:
                        print(e)
                    conn.close()
                    
                    # Send email with the attached image
                    self.send_email(imag_filename)
                
            elif centroid[0] > self.line_end[0]:
                self.id_direction[objectID] = 'out'
                if objectID in self.id_to_unique_id:
                    sql.create_table()
                    base_filename = 'face_image'
                    image_sav_path = Path('./inference/face_image/exit/')
                    
                    if not os.path.exists(image_sav_path):
                        os.makedirs(image_sav_path)
                    
                    # Generate a unique identifier for the person
                    if objectID not in self.id_to_unique_id:
                        unique_id = str(uuid.uuid4())[:8]  # Generate a random UUID and take the first 8 characters
                        self.id_to_unique_id[objectID] = unique_id
                    
                    # Save the image with the unique identifier
                    imag_filename = os.path.join(image_sav_path, f"{base_filename}_{self.id_to_unique_id[objectID]}.jpg")
                    cv2.imwrite(imag_filename, raw_image)
                

        # Count in and out based on the ID direction
        count_in = sum(1 for direction in self.id_direction.values() if direction == 'in')
        count_out = sum(1 for direction in self.id_direction.values() if direction == 'out')
        
        if 0 not in class_ids:
            self.face_count = 0
            self.id_direction = {}

        # Display in and out counts
        cv2.line(im0, self.line_start, self.line_end, (0, 255, 0), 2)
        cv2.putText(im0, f'Count In: {count_in}', (15, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, bottomLeftOrigin=False)
        cv2.putText(im0, f'Count Out: {count_out}', (15, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, bottomLeftOrigin=False)


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
        # Executes object detection on video frames from a specified camera index, plotting bounding boxes and returning modified frames.
        cap = cv2.VideoCapture(self.capture_index)
        assert cap.isOpened()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        frame_count = 0
        # Video Files
        base_filename = 'output'
        direc_save = Path('./frontend/static/output')
        if not os.path.exists(direc_save):
            os.makedirs(direc_save)
        
        # Initialize the counter
        counter = 1
        # Construct the full filename
        full_filename = os.path.join(direc_save, f"{base_filename}_{counter}.mp4")
        
        while os.path.exists(full_filename):
            counter += 1
            full_filename = os.path.join(direc_save, f"{base_filename}_{counter}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        file_result = cv2.VideoWriter(full_filename,fourcc , 20.0, (1280,720))
        while True:
            self.start_time = time()
            ret, im0 = cap.read()
            if ret:
            # Flip the image
                im0 = cv2.flip(im0, 1)
                raw_image = im0.copy()
                results = self.predict(im0)
                im0, class_ids = self.plot_bboxes(results, im0)

                self.line_counter(im0, class_ids, results, raw_image)
                self.display_fps(im0)
                
                file_result.write(im0)
                cv2.imshow('YOLOv8 Detection', im0)

                # Store current frame's class IDs for the next iteration
                self.prev_class_ids = class_ids

                frame_count += 1
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
            else:
                cap.release()
                file_result.release()
                break
        # cv2.destroyAllWindows()

# Define the line start and end points
line_start = (1000, 0)
line_end = (1000, 720)

# Initialize the ObjectDetection instance with the line counter
detector = ObjectDetection(capture_index='F:/AHSS/ahss0001/manasi.mp4', line_start=line_start, line_end=line_end)
detector()
