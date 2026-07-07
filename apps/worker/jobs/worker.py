"""Job worker — optional RQ consumer for pipeline runs."""

from jobs.queue import _connection, queue
from pipeline.ad_pipeline import run_pipeline


def execute_run(brief_id: str, run_id: str):
    run_pipeline(brief_id, run_id, brief_text="")


if __name__ == "__main__":
    from rq import Worker

    worker = Worker([queue], connection=_connection)
    worker.work()
