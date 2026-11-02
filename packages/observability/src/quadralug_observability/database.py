from opentelemetry import trace
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.engine import Engine


def instrument_engine(engine: Engine) -> None:
    SQLAlchemyInstrumentor().instrument(engine=engine, tracer_provider=trace.get_tracer_provider())
