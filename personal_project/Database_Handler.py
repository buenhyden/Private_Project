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

def GCP_MongoDB_Information():
    import pickle
    file = pickle.load(open('./gcp_mongo_User_Information', 'rb'))
    user = file['username']
    password = file['password']
    dbpath = file['dbPath']
    return user, password, dbpath

def LOCALHOST_MongoDB_Information():
    import pickle
    file = pickle.load(open('./localhost_mongo_User_Information','rb'))
    user = file['user']
    password = file['password']
    dbpath = file['webpath']
    return user, password, dbpath

def Use_Database(connection, dbname):
    db = connection[dbname]
    return db

def Use_Collection(db, collectionName):
    collection = db[collectionName]
    return collection

def Close_db(db):
    db.close()
if __name__ == "__main__":
    db_name = 'hy_db'
    mongodb = ToMongoDB(*AWS_MongoDB_Information())
    dbname = db_name
    useDb = Use_Database(mongodb, dbname)