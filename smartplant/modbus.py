"""Holding registers 0..3: temperature*100, vibration*100, rpm, current*100."""
import asyncio
import os

from pymodbus.client import ModbusTcpClient
from pymodbus.datastore import ModbusDeviceContext, ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer

from .simulator import FIELDS, Simulator


class ModbusSource:
    def sample(self):
        with ModbusTcpClient(os.getenv("MODBUS_HOST", "127.0.0.1"),
                             port=int(os.getenv("MODBUS_PORT", "5020")), timeout=2) as client:
            result = client.read_holding_registers(address=0, count=4, device_id=1)
            if result.isError():
                raise RuntimeError(f"Modbus read failed: {result}")
            return dict(zip(FIELDS, [v/s for v, s in zip(result.registers, (100, 100, 1, 100))]))


async def serve():
    sim = Simulator()
    sim.set_mode(os.getenv("SIMULATION_MODE", "normal"))
    device = ModbusDeviceContext(hr=ModbusSequentialDataBlock(0, [0]*10))
    context = ModbusServerContext(devices={1: device}, single=False)

    async def update():
        while True:
            values = sim.sample()
            device.setValues(3, 0, [round(values[k]*s) for k, s in zip(FIELDS, (100, 100, 1, 100))])
            await asyncio.sleep(1)

    task = asyncio.create_task(update())
    try:
        await StartAsyncTcpServer(context=context, address=("0.0.0.0", int(os.getenv("MODBUS_PORT", "5020"))))
    finally:
        task.cancel()


if __name__ == "__main__":
    asyncio.run(serve())
