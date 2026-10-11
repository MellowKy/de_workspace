from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Fargate
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.onprem.analytics import Dbt
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.workflow import Airflow
from diagrams.programming.language import Python

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = WORKSPACE_ROOT / "04_docs" / "architecture_diagrams"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "epdp_architecture"

graph_attr = {
    "fontsize": "16",
    "bgcolor": "white",
    "pad": "0.5",
}

with Diagram(
    name="Enterprise Portable Data Platform (EPDP) Monorepo",
    filename=str(OUTPUT_FILE),
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    with Cluster("Ingestion & Lakehouse Layer"):
        api_stream = Fargate("GitHub REST API")
        raw_buffer = Python("Polars Stream Sinker\n(ZSTD Parquet)")
        lakehouse_db = PostgreSQL("DuckDB OLAP Engine\n(In-Memory / Parquet)")

        api_stream >> Edge(label="NDJSON Buffer") >> raw_buffer
        raw_buffer >> Edge(label="LazyScan") >> lakehouse_db

    with Cluster("Transformation & Modeling"):
        dbt_engine = Dbt("dbt Analytics Core")
        data_marts = PostgreSQL("Kimball Star Schema\n(fct_github_activity)")

        lakehouse_db >> Edge(label="read_parquet()") >> dbt_engine
        dbt_engine >> Edge(label="dbt run / test") >> data_marts

    with Cluster("Orchestration & AI Governance"):
        dagster_sda = Airflow("Dagster Asset Engine")
        vector_catalog = Redis("Qdrant Vector Index\n(Schema & Telemetry)")

        dagster_sda >> Edge(label="Materialize") >> data_marts
        dagster_sda >> Edge(label="Embed Telemetry") >> vector_catalog

    with Cluster("Infrastructure as Code"):
        tf_iac = Python("Terraform 1.9.5 HCL")
        s3_bucket = SimpleStorageServiceS3("AWS S3 Data Lake")

        tf_iac >> Edge(label="terraform validate") >> s3_bucket

print(f"[OK] Visual Architecture Diagram rendered at: {OUTPUT_FILE}.png")
