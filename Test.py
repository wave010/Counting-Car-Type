from configparser import ConfigParser

import pymongo

config = ConfigParser()
config.read("Setting/config.ini")

client = pymongo.MongoClient(config['Config']['Database'])
mydb = client['mydatabase']
mycol = mydb["CountFormVideo"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)