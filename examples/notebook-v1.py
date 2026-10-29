# CELL ********************

import json
from collections.abc import Mapping
from datetime import datetime, timezone

import notebookutils

RELEASE = "v1"
MULTIPLIER = 1


def require_local_lakehouse(context: Mapping[str, object]) -> dict[str, str]:
    binding: dict[str, str] = {}
    for key in (
        "currentWorkspaceName",
        "currentWorkspaceId",
        "defaultLakehouseName",
        "defaultLakehouseId",
        "defaultLakehouseWorkspaceId",
    ):
        value = context.get(key)
        if not isinstance(value, str) or not value:
            raise RuntimeError(f"Required Notebook runtime context is missing: {key}")
        binding[key] = value
    if binding["currentWorkspaceId"].lower() != binding["defaultLakehouseWorkspaceId"].lower():
        raise RuntimeError("Refusing to write to a Lakehouse in a different workspace.")
    if binding["defaultLakehouseName"] != "CI_CD_Demo":
        raise RuntimeError("Attach the stage-local CI_CD_Demo as the default Lakehouse.")
    return binding


binding = require_local_lakehouse(notebookutils.runtime.context)
print(json.dumps(binding, indent=2))

# CELL ********************

from pyspark.sql import functions as F

source = (
    spark.range(10)
    .withColumn("value", F.col("id") * MULTIPLIER)
    .withColumn("release", F.lit(RELEASE))
)
spark.sql(
    "CREATE TABLE IF NOT EXISTS cicd_smoke "
    "(id BIGINT, value BIGINT, release STRING) USING DELTA"
)
source.createOrReplaceTempView("cicd_smoke_source")
spark.sql("""
MERGE INTO cicd_smoke AS target
USING cicd_smoke_source AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET
  target.value = source.value,
  target.release = source.release
WHEN NOT MATCHED THEN INSERT (id, value, release)
VALUES (source.id, source.value, source.release)
""")

# CELL ********************

actual = spark.table("cicd_smoke")
metrics = actual.agg(
    F.count(F.lit(1)).alias("rows"),
    F.countDistinct("id").alias("unique_ids"),
    F.sum("value").alias("sum_value"),
    F.min("id").alias("min_id"),
    F.max("id").alias("max_id"),
    F.countDistinct("release").alias("release_versions"),
    F.min("release").alias("release"),
).first().asDict()
assert metrics["rows"] == 10
assert metrics["unique_ids"] == 10
assert metrics["min_id"] == 0 and metrics["max_id"] == 9
assert metrics["sum_value"] == 45 * MULTIPLIER
assert metrics["release_versions"] == 1 and metrics["release"] == RELEASE
assert [
    row.asDict()
    for row in actual.orderBy("id").select("id", "value", "release").collect()
] == [{"id": i, "value": i * MULTIPLIER, "release": RELEASE} for i in range(10)]
location = spark.sql("DESCRIBE DETAIL cicd_smoke").select("location").first()["location"]
result = {
    "verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
    "workspaceName": binding["currentWorkspaceName"],
    "workspaceId": binding["currentWorkspaceId"],
    "lakehouseName": binding["defaultLakehouseName"],
    "lakehouseId": binding["defaultLakehouseId"],
    "deltaLocation": location,
    **metrics,
}
print(json.dumps(result, indent=2))
display(actual.orderBy("id"))
notebookutils.notebook.exit(json.dumps(result))
