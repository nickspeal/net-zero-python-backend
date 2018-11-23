from app import db
print("Deleting the Database...")
db.drop_all()
print("Creating a new Database...")
db.create_all()
print("Done.")