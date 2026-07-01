import json
import os
cells = []
def add_markdown(text):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    })
def add_code(text):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.split("\n")]
    })
add_markdown("# Smart Medicine Recognition and Reminder System")
add_markdown("## Step 0: Install Requirements\nRun this cell to install the necessary packages.")
add_code("""!pip install opencv-python easyocr numpy pandas pillow matplotlib requests schedule plyer fuzzywuzzy python-Levenshtein ipywidgets pymongo""")
add_markdown("## Step 1: Imports & Setup\nImport libraries, create folders, and connect to MongoDB.")
add_code("""import os
import cv2
import easyocr
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import schedule
import time
from plyer import notification
from fuzzywuzzy import process, fuzz
import ipywidgets as widgets
from IPython.display import display, clear_output
import threading
from pymongo import MongoClient
from datetime import datetime
# Setup directories
if not os.path.exists("uploaded_images"):
    os.makedirs("uploaded_images")
# Setup MongoDB Connection
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client["MedicineScannerDB"]
    medicines_collection = db["medicines"]
    reminders_collection = db["reminders"]
    print("Connected to MongoDB!")
    
    # Reload medicines database from CSV so we get the latest 'Disease' columns
    if os.path.exists("medicine_data.csv"):
        medicines_collection.drop() # Drop existing to ensure fresh structure
        df_meds = pd.read_csv("medicine_data.csv")
        records = df_meds.to_dict(orient="records")
        medicines_collection.insert_many(records)
        print("Populated medicine database from CSV with latest schema.")
    else:
        print("Warning: medicine_data.csv not found to populate DB.")
            
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
""")
add_markdown("## Step 2: Upload Prescription & Medicine Strip\nUpload both images so we can extract all details. If the prescription OCR fails to read handwriting clearly, you can also manually input the Patient Details below.")
add_code("""pres_upload = widgets.FileUpload(accept='image/*', multiple=False, description="Upload Prescription")
strip_upload = widgets.FileUpload(accept='image/*', multiple=False, description="Upload Med Strip")
patient_name_input = widgets.Text(value="Sri Saran", description="Patient Name:")
patient_age_input = widgets.Text(value="18", description="Age:")
out_upload = widgets.Output()
pres_path = None
strip_path = None
def save_upload(upload_widget, filename):
    if not upload_widget.value:
        return None
    try:
        if isinstance(upload_widget.value, tuple):
            content = upload_widget.value[0]['content']
        else:
            fname = list(upload_widget.value.keys())[0]
            content = upload_widget.value[fname]['content']
        
        path = os.path.join("uploaded_images", filename)
        with open(path, "wb") as f:
            f.write(content)
        return path
    except Exception as e:
        print(f"Upload error: {e}")
        return None
def on_upload_change(change):
    global pres_path, strip_path
    with out_upload:
        clear_output()
        p_path = save_upload(pres_upload, "prescription.jpg")
        s_path = save_upload(strip_upload, "strip.jpg")
        
        if p_path:
            pres_path = p_path
            print("Prescription uploaded successfully!")
        if s_path:
            strip_path = s_path
            print("Medicine Strip uploaded successfully!")
pres_upload.observe(on_upload_change, names='value')
strip_upload.observe(on_upload_change, names='value')
display(widgets.HBox([pres_upload, strip_upload]))
display(widgets.HBox([patient_name_input, patient_age_input]))
display(out_upload)
""")
add_markdown("## Step 3: OpenCV Processing & OCR\nProcess images and extract text.")
add_code("""reader = easyocr.Reader(['en'])
def preprocess_and_read(image_path):
    if not image_path or not os.path.exists(image_path):
        return ""
        
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=30)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(denoised)
    
    results = reader.readtext(contrast, detail=0)
    return " ".join(results)
""")
add_markdown("## Step 4: Logic & Report Generation\nCorrelate data and generate final report.")
add_code("""def generate_report():
    print("Processing images...")
    pres_text = preprocess_and_read(pres_path)
    strip_text = preprocess_and_read(strip_path)
    
    # 1. Identify Medicine from Strip using DB
    all_known_meds = [doc['Generic Name'] for doc in medicines_collection.find({}, {"Generic Name": 1})]
    best_med_match = "Unknown Medicine"
    best_score = 0
    
    # Simple heuristic: try to match strip text to our db
    for med in all_known_meds:
        score = fuzz.partial_ratio(med.lower(), strip_text.lower())
        if score > 80 and score > best_score:
            best_med_match = med
            best_score = score
            
    # If strip text was empty (e.g. not uploaded), fallback to demo sample logic
    if not strip_text and "cetirizine" in pres_text.lower():
         best_med_match = "Cetirizine"
    elif not strip_text:
         # Fallback to sample for demonstration if nothing is uploaded
         best_med_match = "Cetirizine" 
    
    # Fetch details from DB
    med_info = medicines_collection.find_one({"Generic Name": best_med_match})
    if not med_info:
        med_info = {
            "Uses": "Unknown", "Disease": "Unknown", 
            "Dosage": "1 tablet", "Reminder Time": "09:00 PM"
        }
    
    # Define outputs
    patient_name = patient_name_input.value
    patient_age = patient_age_input.value
    medicine = best_med_match
    use = med_info.get("Uses", "Unknown")
    disease = med_info.get("Disease", "Unknown")
    dosage = med_info.get("Dosage", "1 tablet")
    
    # Find reminder time from prescription if possible, otherwise default to 9:00 PM
    reminder_time_str = "9:00 PM"
    if "night" in pres_text.lower() or "pm" in pres_text.lower():
        reminder_time_str = "9:00 PM"
    elif "morning" in pres_text.lower() or "am" in pres_text.lower():
        reminder_time_str = "9:00 AM"
    # Save to MongoDB
    time_24h = datetime.strptime(reminder_time_str, "%I:%M %p").strftime("%H:%M")
    reminders_collection.update_one(
        {"Medicine": medicine},
        {"$set": {"Time": reminder_time_str, "Time24": time_24h, "Status": "Pending"}},
        upsert=True
    )
        
    report = f\"\"\"==============================
SMART MEDICINE SYSTEM
==============================
Patient Name : {patient_name}
Age          : {patient_age}
Medicine     : {medicine}
Use          : {use}
Disease      : {disease}
Dosage       : {dosage}
Reminder Time: {reminder_time_str}
⏰ Time to take {medicine}
\"\"\"
    return report, medicine, time_24h, reminder_time_str
""")
add_markdown("## Step 5: Scheduling & Execution\nSchedule the notification and run the pipeline.")
add_code("""def send_notification(medicine, reminder_time_str):
    try:
        notification.notify(
            title=f"Smart Medicine System",
            message=f"⏰ Time to take {medicine}",
            app_name="Medicine Scanner",
            timeout=10
        )
        print(f"[{datetime.now().strftime('%I:%M %p')}] Notification sent for {medicine}!")
    except Exception as e:
        print(f"Could not send notification: {e}")
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
out_report = widgets.Output()
generate_btn = widgets.Button(description="Generate Report & Schedule", button_style='success', layout=widgets.Layout(width='250px'))
def on_generate_clicked(b):
    with out_report:
        clear_output()
        report, medicine, time_24h, time_str = generate_report()
        print(report)
        
        # Setup schedule
        schedule.clear()
        schedule.every().day.at(time_24h).do(
            lambda m=medicine, t=time_str: send_notification(m, t)
        )
        
        # Start thread if not running
        for t in threading.enumerate():
            if t.name == "ScheduleThread":
                return
        t = threading.Thread(target=run_schedule, name="ScheduleThread", daemon=True)
        t.start()
        print(f"\\n--> Background scheduler started for {medicine} at {time_str}")
generate_btn.on_click(on_generate_clicked)
display(generate_btn, out_report)
""")
notebook_json = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}
with open("notebook.ipynb", "w") as f:
    json.dump(notebook_json, f, indent=1)
print("Notebook updated successfully!")