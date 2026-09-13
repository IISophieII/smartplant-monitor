import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .detection import Detector
from .simulator import Simulator
from .storage import Store


class Mode(BaseModel):
    mode: Literal["normal", "progressive_fault"]


def create_app(db_path=None, interval=1.0, source=None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.store = Store(db_path or os.getenv("DATABASE_PATH", "data/smartplant.db"))
        app.state.detector = Detector()
        if source is not None:
            app.state.source = source
        elif os.getenv("DATA_SOURCE", "simulator") == "modbus":
            from .modbus import ModbusSource
            app.state.source = ModbusSource()
        else:
            app.state.source = Simulator()
        app.state.latest = None
        app.state.error = None

        async def collect():
            while True:
                try:
                    if isinstance(app.state.source, Simulator):
                        values = app.state.source.sample()
                    else:
                        values = await asyncio.to_thread(app.state.source.sample)
                    result = await asyncio.to_thread(app.state.detector.evaluate, values)
                    sample = {"timestamp": datetime.now(timezone.utc).isoformat(), "device_id": "motor-01",
                              **values, **result}
                    await asyncio.to_thread(app.state.store.insert, sample)
                    app.state.latest = sample
                    app.state.error = None
                except Exception:
                    logging.exception("Telemetry collection failed")
                    app.state.error = "Collection failed. Retrying; showing the last successful sample, if available."
                await asyncio.sleep(interval)

        task = asyncio.create_task(collect())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    app = FastAPI(title="SmartPlant Monitor", version="0.1.0", lifespan=lifespan)
    static = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(static / "index.html")

    @app.get("/api/health")
    def health():
        return {"status": "degraded" if app.state.error else "ok", "error": app.state.error,
                "ready": app.state.latest is not None}

    @app.get("/api/status")
    def status():
        return {"latest": app.state.latest, "error": app.state.error,
                "source": "simulator" if isinstance(app.state.source, Simulator) else "modbus",
                "mode": getattr(app.state.source, "mode", None)}

    @app.get("/api/history")
    def history(limit: int = Query(120, ge=1, le=3600)):
        return app.state.store.history(limit)

    @app.post("/api/simulation")
    async def simulation(body: Mode):
        if not isinstance(app.state.source, Simulator):
            raise HTTPException(409, "Mode control is available only for the built-in simulator")
        app.state.source.set_mode(body.mode)
        return {"mode": body.mode}

    @app.get("/api/alarms")
    def alarms(limit: int = Query(100, ge=1, le=1000)):
        return app.state.store.alarms(limit)

    @app.post("/api/alarms/{alarm_id}/acknowledge")
    def acknowledge(alarm_id: int):
        if not app.state.store.acknowledge(alarm_id, datetime.now(timezone.utc).isoformat()):
            raise HTTPException(404, "Alarm not found")
        return {"acknowledged": True}

    return app


app = create_app()
