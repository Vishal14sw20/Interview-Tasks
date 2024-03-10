import unittest
import json
from lambda_function import lambda_handler

class TestLambdaFunction(unittest.TestCase):
    def test_event_processing(self):
        event = {
            "Records": [
                {
                    "kinesis": {
                        "data": json.dumps({
                            "event_uuid": "123",
                            "event_name": "account:created",
                            "created_at": 1616161616
                        })
                    }
                }
            ]
        }
        context = {}
        result = lambda_handler(event, context)
        self.assertEqual(result['event_type'], 'account')
        self.assertEqual(result['event_subtype'], 'created')

if __name__ == '__main__':
    unittest.main()
