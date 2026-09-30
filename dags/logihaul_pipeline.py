from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_DIR = "/home/nneoma/logihaul-pipeline"
DBT_DIR = f"{PROJECT_DIR}/dbt_project"
DBT_BIN = f"{PROJECT_DIR}/venv/bin/dbt"


with DAG(
    dag_id="logihaul_pipeline",
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
    tags=["logistics", "etl", "dbt"],
) as dag:

    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=f"cd {PROJECT_DIR} && {PROJECT_DIR}/airflow_venv/bin/python load_raw.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && {DBT_BIN} run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && {DBT_BIN} test",
    )

    load_raw >> dbt_run >> dbt_test
