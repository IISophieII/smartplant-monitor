import os
import socket
import subprocess
import sys
import time

from smartplant.modbus import ModbusSource


def test_real_modbus_tcp_roundtrip(monkeypatch):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    monkeypatch.setenv('MODBUS_PORT', str(port))
    monkeypatch.setenv('MODBUS_HOST', '127.0.0.1')
    process = subprocess.Popen([sys.executable, '-m', 'smartplant.modbus'], env=os.environ.copy(),
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise AssertionError(process.stderr.read().decode())
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=0.1):
                    break
            except OSError:
                time.sleep(0.05)
        sample = ModbusSource().sample()
        assert 40 < sample['temperature'] < 55
        assert 1 < sample['vibration'] < 2
        assert 1400 < sample['rpm'] < 1500
        assert 3 < sample['current'] < 5
    finally:
        process.terminate()
        process.wait(timeout=10)
        process.stderr.close()
