from pymongo import MongoClient
import pandas as pd
import os

def connect_database():

    client = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=3000
    )

    client.server_info()

    db = client["MedicineScannerDB"]
    medicines = db["medicines"]

    if medicines.count_documents({}) == 0:

        print("Importing medicines from CSV...")

        if os.path.exists("medicine_data.csv"):

            df = pd.read_csv("medicine_data.csv")

            print(df.columns)

            medicines.insert_many(df.to_dict("records"))

            print("Medicines imported:", medicines.count_documents({}))

    return medicines