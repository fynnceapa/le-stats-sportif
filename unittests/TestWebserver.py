import unittest
import json
import sys
sys.path.append('../')
from app import webserver

class TestWebserver(unittest.TestCase):
    def setUp(self):
        self.app = webserver.test_client()
        self.app.testing = True
        self.app.config['TESTING'] = True

    def test_states_mean_request(self):
        data = {
            'question': webserver.data_ingestor.get_questions_best_is_min()[0],
            'state': 'Montana'
        }
        response = self.app.post('/api/states_mean', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('job_id', json.loads(response.data))

