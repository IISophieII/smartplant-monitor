from fastapi.testclient import TestClient

from smartplant.app import create_app
from smartplant.storage import Store


def sample(status, second, reasons=None, device='motor-01'):
    return {'timestamp': f'2026-09-13T00:00:{second:02d}+00:00', 'device_id': device,
            'status': status, 'reasons': reasons or []}


def test_alarm_episode_escalation_recovery_and_ack(tmp_path):
    path = tmp_path / 'alarms.db'
    store = Store(path)
    store.insert(sample('normal', 0))
    assert store.alarms() == []
    store.insert(sample('warning', 1, ['baseline']))
    store.insert(sample('warning', 2, ['baseline']))
    alarm = store.alarms()[0]
    assert store.acknowledge(alarm['id'], '2026-09-13T00:00:03+00:00')
    assert store.acknowledge(alarm['id'], '2026-09-13T00:00:04+00:00')
    store.insert(sample('critical', 5, ['temperature']))
    alarm = Store(path).alarms()[0]
    assert alarm['ended_at'] is None
    assert alarm['severity'] == 'critical'
    assert alarm['reasons'] == ['baseline', 'temperature']
    assert alarm['acknowledged_at'].endswith('03+00:00')
    store.insert(sample('normal', 6))
    assert len(store.alarms()) == 1
    assert store.alarms()[0]['ended_at'].endswith('06+00:00')
    store.insert(sample('warning', 7, ['baseline']))
    assert len(store.alarms()) == 2
    assert store.alarms()[0]['acknowledged_at'] is None


def test_devices_and_alarm_api(tmp_path):
    class Offline:
        def sample(self):
            raise OSError('offline')

    with TestClient(create_app(tmp_path/'api.db', source=Offline())) as client:
        store = client.app.state.store
        store.insert(sample('critical', 1, ['temperature']))
        store.insert(sample('warning', 2, ['baseline'], device='motor-02'))
        store.insert(sample('normal', 3))
        alarms = client.get('/api/alarms').json()
        assert len(alarms) == 2
        assert alarms[0]['ended_at'] is None
        assert alarms[1]['ended_at'] is not None
        assert client.post(f"/api/alarms/{alarms[0]['id']}/acknowledge").status_code == 200
        assert client.get('/api/alarms').json()[0]['acknowledged_at'] is not None
        assert client.post('/api/alarms/99999/acknowledge').status_code == 404
        assert client.get('/api/alarms?limit=0').status_code == 422
        assert client.get('/api/alarms?limit=1001').status_code == 422
