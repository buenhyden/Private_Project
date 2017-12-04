import pymongo
def ToMongoDB(username, password, dbPath):
    connection = pymongo.MongoClient('mongodb://{}:{}@{}'.format(username, password, dbPath))
    return connection

def AWS_MongoDB_Information():
    import pickle
    file = pickle.load(open('./aws_mongo_User_Information','rb'))
    user = file['user']
    password = file['password']
    webpath = file['webpath']
    return user, password, webpath

def Use_Database(connection, dbname):
    db = connection[dbname]
    return db

def Use_Collection(db, collectionName):
    collection = db[collectionName]
    return collection

def Close_db(db):
    db.close()
