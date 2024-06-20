import cv2
from scrfd import SCRFD, Threshold
from PIL import Image
import numpy as np
from inference.detect_centroid_tracker import CentroidTracker

class ObjectDetection:
    def __init__(self, capture_index, line_start, line_end):
        self.face_detector = SCRFD.from_path("F:/AHSS/SCRFD/model/scrfd.onnx")
        self.threshold = Threshold(probability=0.4)
        self.capture_index = capture_index
        self.line_start = line_start
        self.line_end = line_end
        self.face_count = 0
        self.human_count = 0
        self.id_direction = {}
        self.id_to_unique_id = {}
        self.prev_class_ids = []
        self.centroid_tracker = CentroidTracker()
        self.previous_positions = {}

    def detect_faces(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(frame)
        faces = self.face_detector.detect(pil_frame, threshold=self.threshold)
        return faces

    def display_fps(self, frame):
        # Display FPS on the frame
        pass  # Placeholder for FPS display

    def line_counter(self, frame, faces, raw_image):
        rects = []
        for face in faces:
            bbox = face.bbox
            rects.append((bbox.upper_left.x, bbox.upper_left.y, bbox.lower_right.x, bbox.lower_right.y))
            self.face_count += 1
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
                if prev_centroid[0] < self.line_start[0] and centroid[0] >= self.line_start[0]:
                    self.id_direction[objectID] = 'in'
                elif prev_centroid[0] >= self.line_start[0] and centroid[0] < self.line_start[0]:
                    self.id_direction[objectID] = 'out'
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

    def __call__(self):
        capture = cv2.VideoCapture(self.capture_index)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while True:
            ret, frame = capture.read()
            if not ret or frame is None:
                break

            # Flip the frame horizontally
            frame = cv2.flip(frame, 1)

            # Detect faces
            faces = self.detect_faces(frame)

            # Process the frame
            self.line_counter(frame, faces, frame)
            self.display_fps(frame)

            # Display the frame
            cv2.imshow("frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        capture.release()
        cv2.destroyAllWindows()

# Define the line start and end points
line_start = (320, 0)
line_end = (320, 480)

# Initialize the ObjectDetection instance with the line counter
detector = ObjectDetection(capture_index=0, line_start=line_start, line_end=line_end)
detector()
