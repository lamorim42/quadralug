import os
import subprocess
import sys
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from quadralug_observability import build_tracer_provider

RESOURCE = {"service.name": "quadralug-bff", "deployment.environment": "test"}


class Collector(ThreadingHTTPServer):
    paths: list[str]


class Handler(BaseHTTPRequestHandler):
    server: Collector

    def do_POST(self) -> None:
        self.rfile.read(int(self.headers["Content-Length"]))
        self.server.paths.append(self.path)
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass


@pytest.fixture
def collector() -> Iterator[Collector]:
    server = Collector(("127.0.0.1", 0), Handler)
    server.paths = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


def span_exporters(provider: TracerProvider) -> list[Any]:
    processors = provider._active_span_processor._span_processors
    return [processor.span_exporter for processor in processors]


@pytest.mark.parametrize("suffix", ["", "/"], ids=["sem-barra", "com-barra"])
def test_otlp_exports_spans_to_the_endpoint(collector: Collector, suffix: str) -> None:
    endpoint = f"http://127.0.0.1:{collector.server_port}{suffix}"
    provider = build_tracer_provider(RESOURCE, {"OTEL_EXPORTER_OTLP_ENDPOINT": endpoint})

    with provider.get_tracer("t").start_as_current_span("s"):
        pass
    provider.force_flush()

    assert collector.paths == ["/v1/traces"]
    provider.shutdown()


def test_otlp_configure_observability_reads_environment(collector: Collector) -> None:
    script = (
        "from fastapi import FastAPI\n"
        "from opentelemetry import trace\n"
        "from quadralug_observability import configure_observability\n"
        "configure_observability(FastAPI(), 'quadralug-bff')\n"
        "with trace.get_tracer('t').start_as_current_span('s'):\n"
        "    pass\n"
        "trace.get_tracer_provider().force_flush()\n"
    )
    env = {
        **os.environ,
        "OTEL_EXPORTER_OTLP_ENDPOINT": f"http://127.0.0.1:{collector.server_port}",
    }

    subprocess.run([sys.executable, "-c", script], env=env, check=True)

    assert collector.paths == ["/v1/traces"]


def test_otlp_exporter_created_when_defined() -> None:
    provider = build_tracer_provider(
        RESOURCE, {"OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:4318"}
    )

    exporters = span_exporters(provider)

    assert len(exporters) == 1
    assert isinstance(exporters[0], OTLPSpanExporter)
    provider.shutdown()


@pytest.mark.parametrize(
    "environ", [{}, {"OTEL_EXPORTER_OTLP_ENDPOINT": ""}, {"OTEL_EXPORTER_OTLP_ENDPOINT": "  "}]
)
def test_otlp_exporter_absent_when_undefined(environ: dict[str, str]) -> None:
    provider = build_tracer_provider(RESOURCE, environ)

    exporters = span_exporters(provider)

    assert exporters == []
