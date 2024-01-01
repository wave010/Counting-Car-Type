import pandas as pd
import pymongo
#
# # Create a new client and connect to the server
uri = "mongodb+srv://thirawat:1234@cluster0.1h6mdye.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(uri)
mydb = client['mydatabase']
#
# # # --------------------------------------------
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

    # add data to collection
    mycol = mydb["CountFormVideo"]
    df = pd.read_csv("SourceData/countting_.csv")
    my_dict_log = df.to_dict(orient='records')
    my_dict_data = {
        "Path": "//D/lower",
        'fps': 29.12,
        'total frame': 590,
        'duration (s)': 2345,
        'start_count': 123,
        'end_count': 234,
        'Log': my_dict_log
    }
    x = mycol.insert_one(my_dict_data)
    print("Successfully inserted into the database.")
except Exception as e:
    print(f"An error occurred: {type(e).__name__} - {e}")