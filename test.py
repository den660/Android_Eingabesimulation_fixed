import unittest
from dao import MySQLDAO

class TestDAO(unittest.TestCase):
    def test_dao(self):
        dao = MySQLDAO()
        dao.connect()
        record_id = dao.create_record("unittest")
        input_id = dao.create_input(record_id, 1000)
        dao.create_event(input_id, 10, 9, 8, 7)

        records = dao.get_records()
        test_record = records[len(records) - 1]
        self.assertEqual(test_record.title, "unittest")
        self.assertEqual(test_record.id, record_id)

        inputs = dao.get_inputs(record_id)
        test_input = inputs[len(inputs) - 1]
        self.assertEqual(test_input.delay, 1000)
        self.assertEqual(test_input.id, input_id)

        events = dao.get_events(input_id)
        test_event = events[len(events) - 1]
        self.assertEqual(test_event.device, 10)
        self.assertEqual(test_event.type, 9)
        self.assertEqual(test_event.code, 8)
        self.assertEqual(test_event.value, 7)

        dao.delete_record(record_id)
        dao.close_connection()

if __name__ == '__main__':
    unittest.main()