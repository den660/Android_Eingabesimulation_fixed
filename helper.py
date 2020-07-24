class Record():
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.inputs = []



class Input():
    def __init__(self, id, delay):
        self.id = id
        self.delay = delay
        self.events = []
        self.record_id = None

class Event():
    def __init__(self, device, type, code, value, input_id=None):
        self.device = device
        self.type = type
        self.code = code
        self.value = value
        self.input_id = input_id

