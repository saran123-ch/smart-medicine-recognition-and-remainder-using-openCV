
# Smart Medicine Recognition and Reminder System using OpenCV

## Project Overview
The Smart Medicine Recognition and Reminder System is an AI-based application that recognizes medicine strips using Optical Character Recognition (OCR). It identifies the medicine name and displays important details such as its uses, dosage, disease, and side effects. The system can also be extended to provide medicine reminders based on a doctor's prescription.

## Features
- Detects medicine names from images using OCR.
- Matches medicines with a medicine database.
- Displays medicine information:
  - Medicine Name
  - Uses
  - Disease
  - Dosage
  - Side Effects
- Stores medicine information in a CSV database.
- User-friendly and easy to use.
- Can be extended to provide automatic medicine reminders.

## Technologies Used
- Python
- OpenCV
- EasyOCR
- Pandas
- Git & GitHub

## Project Structure
```
Medicine Recognition/
│── main.py
│── ocr.py
│── matcher.py
│── database.py
│── medicine_data.csv
│── requirements.txt
│── uploaded_images/
│── notebook.ipynb
```

## Installation

1. Clone the repository
```bash
git clone https://github.com/saran123-ch/smart-medicine-recognition-and-remainder-using-openCV.git
```

2. Install the required packages
```bash
pip install -r requirements.txt
```

3. Run the project
```bash
python main.py
```

## Future Enhancements
- Automatic medicine reminder notifications.
- Scan doctor's prescription and extract medicines automatically.
- Support handwritten prescriptions.
- Mobile application support.
- Cloud database integration.

## Author
**Sri Saran**
