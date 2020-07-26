import mysql.connector
from helper import Record, Input, Event
from error import show_error

class MySQLDAO():
    def __init__(self):
        pass

    def connect(self):
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="",
                database="android_records"
            )
        except:
            show_error("Connection to Database failed")
        self.mycursor = self.mydb.cursor()

    def create_database(self):
        self.mycursor.execute("CREATE DATABASE Android_Records")

    def create_tables(self):
        self.mycursor.execute("CREATE TABLE Record ("
                         "RecordID integer NOT NULL AUTO_INCREMENT,"
                         "Title varchar(100),"
                         "Date datetime,"
                         "PRIMARY KEY (RecordID))")
        self.mycursor.execute("CREATE TABLE Input("
                         "InputID integer NOT NULL AUTO_INCREMENT,"
                         "RecordID integer NOT NULL,"
                         "Delay integer,"
                         "PRIMARY KEY (InputID),"
                         "FOREIGN KEY (RecordID) REFERENCES Record(RecordID) ON DELETE CASCADE)")
        self.mycursor.execute("CREATE TABLE Event("
                         "EventID integer NOT NULL AUTO_INCREMENT,"
                         "InputID integer NOT NULL,"
                         "Device integer,"
                         "Type integer,"
                         "Code integer,"
                         "Value integer,"
                         "PRIMARY KEY (EventID),"
                         "FOREIGN KEY (InputID) REFERENCES Input(InputID) ON DELETE CASCADE)")
    def create_record(self, title):
        #print("INSERT INTO Record (Title,Date) VALUES ('%s', NOW())" % title)
        self.mycursor.execute("INSERT INTO Record (Title,Date) VALUES ('%s', NOW())" % title)
        self.mydb.commit()
        self.mycursor.execute("SELECT MAX(RecordID) FROM Record")
        return int(self.mycursor.fetchone()[0])

    def create_input(self, recordid, delay):
        print(recordid, delay)
        print("INSERT INTO Input (RecordID,Delay) VALUES (%d, %d)" % (recordid, delay))
        self.mycursor.execute("INSERT INTO Input (RecordID,Delay) VALUES (%d, %d)" % (recordid, delay))
        self.mydb.commit()
        self.mycursor.execute("SELECT MAX(InputID) FROM Input")
        return self.mycursor.fetchone()[0]

    def create_event(self, inputid, device, type, code, value):
        print("INSERT INTO Event (InputID,Device,Type,Code,Value) VALUES (%d, %d, %d, %d, %d)" % (inputid, device, type, code, value))
        self.mycursor.execute("INSERT INTO Event (InputID,Device,Type,Code,Value) VALUES (%d, %d, %d, %d, %d)" % (inputid, device, type, code, value))

    def commit_events(self):
        self.mydb.commit()

    def get_records(self):
        print("SELECT RecordID,Title FROM Record")
        self.mycursor.execute("SELECT RecordID,Title FROM Record")
        records = []
        for record in self.mycursor.fetchall():
            records.append(Record(record[0], record[1]))
        return records
    def get_inputs(self, record_id):
        self.mycursor.execute("SELECT InputID,Delay FROM INPUT WHERE RecordID=%d" % record_id)
        inputs = []
        for input in self.mycursor.fetchall():
            inputs.append(Input(input[0], input[1]))
        return inputs

    def delete_record(self, record_id):
        print("DELETE FROM Record WHERE RecordID=%d" % record_id)
        self.mycursor.execute("DELETE FROM Record WHERE RecordID=%d" % record_id)
        self.mydb.commit()

    def delete_input(self, input_id):
        print("DELETE FROM Record WHERE RecordID=%d" % input_id)
        self.mycursor.execute("DELETE FROM Input WHERE InputID=%d" % input_id)
        self.mydb.commit()

    def update_input_delay(self, input_id, delay):
        self.mycursor.execute("UPDATE Input SET Delay=%d WHERE InputID=%d" % (delay, input_id))
        self.mydb.commit()

    def get_highest_record_id(self):
        self.mycursor.execute("SELECT MAX(RecordID) FROM Record")
        id = self.mycursor.fetchone()[0]
        if id == None:
            return -1
        else:
            return id

    def get_highest_input_id(self):
        self.mycursor.execute("SELECT MAX(InputID) FROM Input")
        id = self.mycursor.fetchone()[0]
        if id == None:
            return -1
        else:
            return id

    def integrate_record(self, target_record_id, source_record_id, target_input_id):
        print("from "+str(source_record_id)+" to "+str(target_record_id)+" input "+str(target_input_id))
        self.mycursor.execute("INSERT INTO Input (RecordID,Delay) (SELECT RecordID, Delay FROM Input WHERE RecordID=%d)" % source_record_id)

    def get_events(self, input_id):
        self.mycursor.execute("SELECT Device, Type, Code, Value FROM Event WHERE InputID=%d" % input_id)
        events = []
        for event in self.mycursor.fetchall():
            events.append(Event(event[0], event[1], event[2], event[3], input_id))
        return events

    def is_record_title_available(self, record_title):
        self.mycursor.execute("SELECT * FROM Record WHERE Title='%s'" % record_title)
        if self.mycursor.fetchone() == None:
            return True
        else:
            return False

    def close_connection(self):
        self.mydb.close()


if __name__ == '__main__':
    dao = MySQLDAO()
    dao.connect()
    dao.create_tables()
    dao.close_connection()