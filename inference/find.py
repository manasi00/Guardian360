from deepface import DeepFace as df
import os
import cv2
from pathlib import Path
import datetime as dt
import sql

def find_faces(img_path, db_path):
    result = df.find(img_path = img_path, db_path = db_path, model_name = 'VGG-Face', enforce_detection = True, detector_backend = 'mtcnn')
    return result

while True:
    fold_path = "./inference/static/face_image/"
    for file in os.listdir(os.path.join(fold_path, 'out')):
        if file.endswith('.jpg'):
            try:
                result = find_faces(os.path.join(fold_path, 'out', file), os.path.join(fold_path, 'in'))
                for i in range(len(result[0]['identity'])):
                    print(Path(result[0]['identity'][i]))
                
                if result[0]['identity'][0]:
                    im_path = result[0]['identity'][0]
                    print(im_path)
                    file_name = Path(im_path)
                    file_name = os.path.basename(im_path)
                    # file_name = 'f'+file_name
                    ifm = im_path + ' ' + file_name
                    with open('log', 'w') as f:
                        f.write(ifm)    
                    new_path = "./frontend/static/events/"
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    im_copy = cv2.imread(im_path)
                    cv2.imwrite(new_path+file, im_copy)
                    
                    conn = sql.create_connection()             
                    cursor = conn.cursor()
                    query = "UPDATE Events SET face_path=?, exited_at = ? WHERE face_path = ?"
                    cursor.execute(query, (file, dt.datetime.now(), file_name))
                    conn.commit()
                    os.remove(os.path.join(fold_path, 'out', file))
                    os.remove(im_path)
                    conn.close()
                
            except Exception as e:
                print(e)