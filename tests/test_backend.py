import unittest

from backend.main import app


class BackendApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_overview_endpoint(self):
        response = self.client.get('/api/overview')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('total_observations', payload)
        self.assertIn('average_pm25', payload)
        self.assertIn('most_common_aqi_category', payload)

    def test_aqi_endpoint(self):
        response = self.client.get('/api/aqi')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 0)

    def test_pm25_endpoint(self):
        response = self.client.get('/api/pm25')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 0)

    def test_stations_endpoint(self):
        response = self.client.get('/api/stations')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 0)

    def test_dataset_endpoint(self):
        response = self.client.get('/api/dataset-info')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('records', payload)
        self.assertIn('stations', payload)

    def test_data_page_endpoint(self):
        response = self.client.get('/api/data?page=1&page_size=10')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('items', payload)
        self.assertIn('total_pages', payload)

    def test_monitoring_snapshot_uses_station_averages(self):
        response = self.client.get('/api/live-monitoring')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['mode'], 'historical_hadoop_output')
        self.assertEqual(payload['stations_analyzed'], 107)
        self.assertEqual(payload['highest_station']['station_id'], 'DL002')
        self.assertEqual(payload['pm25_threshold'], 100)
        self.assertEqual(len(payload['top_stations']), 5)


if __name__ == '__main__':
    unittest.main()
