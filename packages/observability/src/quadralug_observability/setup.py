import logging
import os
import sys
from collections.abc import Mapping

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from quadralug_observability.formatter import JsonFormatter
from quadralug_observability.middleware import RequestLogMiddleware


def build_resource(service_name: str, environ: Mapping[str, str]) -> dict[str, str]:
    return {
        "service.name": service_name,
        "deployment.environment": environ.get("DEPLOYMENT_ENVIRONMENT", "dev"),
    }


def build_tracer_provider(
    resource: Mapping[str, str], environ: Mapping[str, str]
) -> TracerProvider:
    provider = TracerProvider(resource=Resource.create(dict(resource)))
    endpoint = environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if endpoint:
        exporter = OTLPSpanExporter(endpoint=f"{endpoint.rstrip('/')}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
    return provider


def configure_observability(app: FastAPI, service_name: str) -> None:
    resource = build_resource(service_name, os.environ)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(resource))
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    provider = build_tracer_provider(resource, os.environ)
    trace.set_tracer_provider(provider)

    app.add_middleware(RequestLogMiddleware)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
