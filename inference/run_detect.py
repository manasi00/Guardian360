import subprocess
import sql
import cv2
import time
import os

detect_process = None

def handle_signal():
    global detect_process
    global save_video_process
    global find_process
    if detect_process:
        detect_process.kill()
        print("Detect process terminated.")
        save_video_process.kill()
        print("Save video process terminated.")
        find_process.kill()
        print("Find process terminated.")

def handle_url():
    global detect_process
    global save_video_process
    global find_process
    old_url = None
    new_url = None
    
    while True:
        new_url = sql.get_url()
        if new_url is None:
            print("No URL available.")
            time.sleep(5)
            continue
        if new_url != old_url:
            handle_signal()
            
            if is_video_stream_available(new_url):
                detect_process = subprocess.Popen(['python', 'inference/detect.py', new_url])
                print(f"Detect process started for URL: {new_url}")
                save_video_process = subprocess.Popen(['python', 'inference/save_video.py', new_url])
                print(f"Save video process started for URL: {new_url}")
                find_process = subprocess.Popen(['python', 'inference/find.py'])
                print(f"Face Matching Process started for detected face")
            else:
                print(f"No video stream available at URL: {new_url}")
            
            old_url = new_url
        
        time.sleep(5)

def is_video_stream_available(url, timeout=10):
    if 'media/video' in url and url.endswith('.mp4'):
        return True
    cap = cv2.VideoCapture(url)
    start_time = time.time()
    
    while True:
        ret, _ = cap.read()
        if ret:
            cap.release()
            return True
        
        if time.time() - start_time > timeout:
            cap.release()
            return False
        
        time.sleep(0.5)


if __name__ == '__main__':
    handle_url()