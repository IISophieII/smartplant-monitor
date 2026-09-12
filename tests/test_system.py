import time

from fastapi.testclient import TestClient

from smartplant.app import create_app
from smartplant.detection import Detector
from smartplant.simulator import Simulator
from smartplant.storage import Store


def test_fault_and_recovery():
    sim, detector = Simulator(17), Detector()
    normal = [detector.evaluate(sim.sample())["status"] for _ in range(100)]
    assert normal.count("normal") >= 85
    sim.set_mode("progressive_fault")
    for _ in range(60):
        values = sim.sample()
    result = detector.evaluate(values)
    assert result["status"] == "critical"
    assert result["health"] <= 25
    assert len(result["reasons"]) == 3
    sim.set_mode("normal")
    assert sim.sample()["temperature"] < 55


def test_store_persists_in_chronological_order(tmp_path):
    path = tmp_path / "telemetry.db"
    store = Store(path)
    for i in range(5):
        store.insert({"temperature": i})
    assert [s["temperature"] for s in Store(path).history(3)] == [2, 3, 4]


def wait_ready(client):
    for _ in range(100):
        if client.get('/api/status').json()['latest']:
            return
        time.sleep(0.02)
    raise AssertionError('No sample arrived')


def test_api_lifecycle(tmp_path):
    with TestClient(create_app(tmp_path / "test.db", interval=0.01)) as client:
        wait_ready(client)
        assert client.get('/').status_code == 200
        assert client.get('/static/app.js').status_code == 200
        assert client.get('/api/health').json()['ready']
        assert client.get('/api/history?limit=0').status_code == 422
        assert client.get('/api/history?limit=3601').status_code == 422
        assert client.post('/api/simulation', json={'mode': 'bad'}).status_code == 422
        assert client.post('/api/simulation', json={'mode': 'progressive_fault'}).status_code == 200
        assert client.get('/api/status').json()['mode'] == 'progressive_fault'
        assert len(client.get('/api/history').json()) >= 1


def test_source_failure_and_mode_rejection(tmp_path):
    class Broken:
        def sample(self):
            raise OSError('disconnected')
    with TestClient(create_app(tmp_path / 'broken.db', source=Broken(), interval=0.01)) as client:
        for _ in range(100):
            if client.get('/api/health').json()['error']:
                break
            time.sleep(0.01)
        assert client.get('/api/health').json()['status'] == 'degraded'
        assert client.get('/api/status').json()['latest'] is None
        assert client.post('/api/simulation', json={'mode': 'normal'}).status_code == 409


def test_collection_recovers_without_restart(tmp_path):
    class Recovering:
        failing = True

        def sample(self):
            if self.failing:
                raise OSError('offline')
            return {'temperature': 48, 'vibration': 1.3, 'rpm': 1450, 'current': 3.8}

    source = Recovering()
    with TestClient(create_app(tmp_path / 'recovery.db', source=source, interval=0.01)) as client:
        for _ in range(100):
            if client.get('/api/health').json()['error']:
                break
            time.sleep(0.01)
        assert client.get('/api/health').json()['error']
        source.failing = False
        wait_ready(client)
        assert client.get('/api/health').json()['error'] is None
        assert client.get('/api/status').json()['latest']['temperature'] == 48
