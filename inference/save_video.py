import cv2
import os
import datetime
import time
import sys

def save_video(url, segment_time=60):
    video_path = "media/video/"
    if not os.path.exists(video_path):
        os.makedirs(video_path)

    cap = cv2.VideoCapture(url)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:  # Fallback if FPS retrieval fails
        fps = 15
        print("Warning: FPS retrieval failed. Using default FPS of 15.")
    
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    # Try different codecs
    codecs = ['avc1', 'h264', 'x264', 'mp4v']
    fourcc = None
    for codec in codecs:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        temp_filename = 'test.mp4'
        temp_out = cv2.VideoWriter(temp_filename, fourcc, fps, (width, height))
        if temp_out.isOpened():
            temp_out.release()
            os.remove(temp_filename)
            print(f"Using codec: {codec}")
            break
        else:
            print(f"Codec {codec} not available, trying next...")
    
    if fourcc is None:
        print("No suitable codec found. Video cannot be saved.")
        return

    start_time = time.time()
    out = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Check if we need to start a new video segment
        if elapsed_time > segment_time or out is None:
            if out is not None:
                out.release()
            video_filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".mp4"
            out = cv2.VideoWriter(os.path.join(video_path, video_filename), fourcc, fps, (width, height))
            start_time = current_time
            print(f"Started new video segment: {video_filename}")

        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()
    print("Video capture ended.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
        save_video(url)
    else:
        print("Please provide a URL as an argument.")