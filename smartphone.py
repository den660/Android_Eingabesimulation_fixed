import threading
import subprocess
import re
import time
from dao import MySQLDAO
from helper import Record, Input, Event
from error import show_error

class Smartphone:
    dao = MySQLDAO()
    thread = None
    def __init__(self, id, status):
        self.id = id
        self.status = status
        self.stop_flag = True
        self.proc = subprocess
        self.all_dao_requests = 0

    def __str__(self):
        return self.id + "   " + self.status

    def get_id(self):
        return self.id
    
    def get_status(self):
        return self.status

    def start_record(self, frame):
        print("start record")
        self.frame = frame
        Smartphone.dao.connect()
        self.input_start_index = Smartphone.dao.get_highest_input_id() + 1
        if self.stop_flag == True:
            self.record = Record(Smartphone.dao.get_highest_record_id() + 1, "placeholder")
            self.stop_flag = False
            Smartphone.thread = threading.Thread(target=self.recorder)
            Smartphone.thread.start()
        Smartphone.dao.close_connection()


    def stop_record(self, record_title):
        if self.stop_flag == False:
            print("stop record")
            self.record.title = record_title
            self.stop_flag = True
            self.proc.kill()
            #Smartphone.thread.join()
            print("thread killed")

    def commit_record(self):
        dao_requests_done=0
        Smartphone.dao.connect()
        record_id = Smartphone.dao.create_record(self.record.title)
        print("recordid: " + str(record_id))
        for input in self.record.inputs:
            input_id = Smartphone.dao.create_input(record_id, input.delay)
            dao_requests_done+=1
            for event in input.events:
                Smartphone.dao.create_event(input_id, event.device, event.type, event.code, event.value)
                dao_requests_done+=1
                print(str(dao_requests_done) + "/" + str(self.all_dao_requests))
                self.frame.update_text_box(str(dao_requests_done) + "/" + str(self.all_dao_requests))
            Smartphone.dao.commit_events()
        print("committed")
        self.frame.update_text_box("committed")
        Smartphone.dao.close_connection()
        self.all_dao_requests = 0

    def replay(self, record):
        all_events = 0
        event_counter = 0
        Smartphone.dao.connect()
        inputs = Smartphone.dao.get_inputs(record.id)
        for input in inputs:
             events= Smartphone.dao.get_events(input.id)
             input.events = events
             all_events += len(events)
        Smartphone.dao.close_connection()
        for input in inputs:
            #time.sleep(input.delay / 1000)
            for event in input.events:
                subprocess.run("platform-tools/adb -s " + self.id + " shell sendevent /dev/input/event" + str(event.device) +" "+ str(event.type) +" "+ str(event.code) +" "+ str(event.value))
                print(str(event_counter) + "/" + str(all_events))
                event_counter += 1



    def recorder(self):
        print("thread start")
        while True:
            if self.stop_flag is True:
                print("stop")
                break
            start = time.time()
            input_counter = 0
            line_buffer = []
            self.proc = subprocess.Popen("platform-tools/adb -s " + self.id + " shell getevent", stdout=subprocess.PIPE)
            for line in iter(self.proc.stdout.readline, b""):

                line = line.decode("utf-8").replace("\r","").replace("\n","")
                print(line)
                self.frame.update_text_box(line)
                if line[0] == "/" and len(line) > 36:
                    event_data = line.split()
                    tmpdict = {
                        "device": int(re.findall(r"\d+",event_data[0])[0]),
                        "type": int(event_data[1], 16),
                        "code": int(event_data[2], 16),
                        "value": int(event_data[3], 16),
                    }
                    line_buffer.append(tmpdict)
                    if tmpdict["type"] == 0 and tmpdict["code"] == 0:
                        millis = int(round((time.time() - start)*1000))
                        #millis = 10
                        start = time.time()
                        #input_id = self.input_start_index + input_counter
                        input = Input(None,millis)
                        input.record_id = self.record.id
                        self.all_dao_requests += 1
                        for dic in line_buffer:
                            input.events.append(Event(dic["device"], dic["type"], dic["code"], dic["value"]))
                            self.all_dao_requests += 1
                        self.record.inputs.append(input)
                        input_counter += 1
            self.commit_record()