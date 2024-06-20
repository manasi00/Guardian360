# Guardian360
----
Clone the repo
```
git clone https://github.com/manasi00/Guardian360.git
```

cd into repo
```
cd Guardian360
```

Run Once
----
Create virtual environment
```
python -m venv ahss0001
```

Activate virtual environment
----
```
Set-ExecutionPolicy Unrestricted -Scope Process
./ahss0001/Scripts/activate
```

Install requirements
----
```
pip install -r requirements.txt
```

Run Migrations
----
```
python manage.py makemigrations
python manage.py migrate
```

Run Server
----
```
python manage.py runserver
```

Project Structure:
----    
    .
    ├── ...
    ├── frontend                                  # Contains all frontend files
    │   ├── static                                # All static file including css, js and images
    │   ├── templates                             # Contains all template files 
    │   └── ...                                   # Other Python Scripts
    ├── inference                                 # Contains all inference files
    │   ├── static                                # All static file like images
    │   ├── templates                             # Contains all template files
    │   ├── detect_centroid_tracker.py            # Face tracker based on centroid formula
    │   ├── detect.py                             # Contains face detection scripts using scrfd model
    │   ├── find.py                               # Contains face finding scripts using deepface vgg-face model
    │   ├── save_video.py                         # Save the live vide
    │   └── ...                                   # Other Python Scripts
    ├── static                                    # Contains models
    └── ...
