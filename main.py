from datetime import datetime
import winsound
import time
from tkinter import Tk, messagebox
from database import connect_database
from ocr import preprocess_and_read
from matcher import find_best_match
import threading
import winsound
import os

print("=" * 60)
print(" SMART MEDICINE RECOGNITION SYSTEM ")
print("=" * 60)

# Connect Database
medicines = connect_database()

# Read Medicine Strip
import os

print("\nAvailable Medicine Images:\n")

image_files = []

for file in os.listdir("uploaded_images"):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        image_files.append(file)
        print("•", file)

print()

medicine_name = input("Enter medicine name: ").strip().lower()

image_path = None

for file in image_files:
    filename = os.path.splitext(file)[0].lower()

    # Allow partial matching
    if medicine_name in filename:
        image_path = os.path.join("uploaded_images", file)
        break
    print("\nAvailable Medicine Images:\n")

image_files = []

for file in os.listdir("uploaded_images"):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        image_files.append(file)
        print("•", file)

print()
medicine_name = input("Enter medicine name: ").strip().lower().replace(" ", "")

image_path = None

for file in image_files:
    filename = os.path.splitext(file)[0].lower().replace(" ", "")

    if medicine_name in filename:
        image_path = os.path.join("uploaded_images", file)
        break

if image_path is None:
    print("\n❌ Medicine image not found.")
    exit()

ocr_text = preprocess_and_read(image_path)

ocr_text = preprocess_and_read(image_path)

print("\n========== OCR OUTPUT ==========\n")
print(ocr_text)

# Find Best Match
best_medicine, score = find_best_match(ocr_text, medicines)
print("\n========== MATCH RESULT ==========\n")
if best_medicine:

    print("Medicine Found :", best_medicine["Generic Name"])
    print("Confidence     :", round(score * 100, 2), "%")

    print("Uses               :", best_medicine.get("Uses", "Not Available"))
    print("Disease            :", best_medicine.get("Disease", "Not Available"))
    print("Dosage             :", best_medicine.get("Dosage", "Not Available"))
    print("Side Effects       :", best_medicine.get("Side Effects", "Not Available"))
    print("Warnings           :", best_medicine.get("Warnings", "Not Available"))
    print("Storage            :", best_medicine.get("Storage", "Not Available"))

    food = best_medicine.get("Food Restrictions")

    if str(food) == "nan":
        food = "None"

    print("Food Restrictions  :", food)
    # ---------------- Patient Details ----------------

patient_name = input("\nEnter Patient Name: ")
patient_age = input("Enter Age: ")
reminder_time = input("Enter Reminder Time (HH:MM AM/PM): ")
reminder_time = datetime.strptime(
    reminder_time,
    "%I:%M %p"
).strftime("%I:%M %p")
print("\n===================================")
print(" SMART MEDICINE SYSTEM ")
print("===================================\n")

print("Patient Name :", patient_name)
print("Age          :", patient_age)
print("\nMedicine :", best_medicine["Generic Name"])
print("Uses :", best_medicine["Uses"])
print("Disease :", best_medicine["Disease"])
print("Dosage :", best_medicine["Dosage"])

print("\nReminder Time:", reminder_time)

print("\n⏰ Time to take", best_medicine["Generic Name"])

print("\n===================================")
while True:
    current_time = datetime.now().strftime("%I:%M %p")
    print("Current:", current_time, "| Reminder:", reminder_time)

    if current_time == reminder_time:

        def alarm():
            for i in range(10):
                winsound.Beep(1000, 1000)

        threading.Thread(target=alarm).start()

        root = Tk()
        root.withdraw()

        messagebox.showinfo(
            "💊 Medicine Reminder",
            f"⏰ Time to take {best_medicine['Generic Name']}"
        )

        root.destroy()
        break

    time.sleep(1)
