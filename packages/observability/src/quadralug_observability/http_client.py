from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


def instrument_http_clients() -> None:
    HTTPXClientInstrumentor().instrument()
