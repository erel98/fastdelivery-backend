from DBManager import DBManager
import bcrypt

# DISCLAIMER!!: This helper class was first implemented in my CPP project by me.
class DBSeed:
    
    def createUsersTable(self):
        region = 'us-east-1'
        d = DBManager()
        
        table_name="users"
        
        key_schema=[
            {
                "AttributeName": "id",
                "KeyType": "HASH"
            }
        ]
        
        attribute_definitions=[
            {
                "AttributeName": "id",
                "AttributeType": "S"
            }
            
        ]
        
        provisioned_throughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1
        }
        
        d.create_table(table_name, key_schema, attribute_definitions, provisioned_throughput, region)
    
    def seedUsersTable(self):
        region = 'us-east-1'
        d = DBManager()
        
        table_name="users"
        password = bcrypt.hashpw(b'test123', bcrypt.gensalt())
        item = {
            'id': '1',
            'fullName': 'Erel Ozturk',
            'age': int(25),
            'gender': (1),
            'imageUrl': '',
            'mobile': '0831104840',
            'username': 'erel_ozturk',
            'email': 'erelozturk98@gmail.com',
            'password': password
        }
        
        d.store_an_item(region, table_name, item)
    
    def createAvailabilityTable(self):
        region = 'us-east-1'
        d = DBManager()
        
        table_name="availabilities"
        
        key_schema=[
            {
                "AttributeName": "id",
                "KeyType": "HASH"
            }
        ]
        
        attribute_definitions=[
            {
                "AttributeName": "id",
                "AttributeType": "S"
            }
            
        ]
        
        provisioned_throughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1
        }
        
        d.create_table(table_name, key_schema, attribute_definitions, provisioned_throughput, region)
    
    def seedAvailabilityTable(self):
        region = 'us-east-1'
        d = DBManager()
        
        table_name="availabilities"
        
        item = {
            'id': '1',
            'user_id': '1',
            'dayOfWeek': 2,
            'fromTime': '08:00',
            'toTime': '18:00'
        }
        
        d.store_an_item(region, table_name, item)
    
    def createDeliveryTable(self):
        region = 'us-east-1'
        d = DBManager()
        
        table_name="deliveries"
        
        key_schema=[
            {
                "AttributeName": "id",
                "KeyType": "HASH"
            }
        ]
        
        attribute_definitions=[
            {
                "AttributeName": "id",
                "AttributeType": "S"
            }
            
        ]
        
        provisioned_throughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1
        }
        
        d.create_table(table_name, key_schema, attribute_definitions, provisioned_throughput, region)
        
def main():
    dbseed = DBSeed()
    
    #dbseed.createUsersTable()
    
    #dbseed.seedUsersTable()
    
    #dbseed.createAvailabilityTable()
    
    #dbseed.seedAvailabilityTable()
    
    dbseed.createDeliveryTable()

if __name__ == '__main__':
    main()
    