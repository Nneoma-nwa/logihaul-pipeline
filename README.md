Raw Data Quality Baseline

The synthetic LogiHaul source data intentionally contains data-quality issues representative of operational systems, including missing values, duplicate identifiers, invalid foreign keys, negative costs, and temporal inconsistencies. These issues are preserved in the raw layer and are addressed during downstream transformation and validation.

Then we can eventually show:

RAW                         MART
────────────────────────────────────
110 missing phones     →    0
duplicate IDs          →    resolved
invalid vehicle FKs    →    flagged/removed
negative costs         →    corrected/removed
invalid timestamps     →    handled

That becomes proof of what your pipeline actually accomplished.

1. The dbt test itself — the YAML test description is documentation:

yaml
- dbt_utils.expression_is_true:
    expression: "actual_delivery_time >= scheduled_time - interval '15 minutes'"
    config:
      description: >
        Flags deliveries where actual_delivery_time is earlier than scheduled_time
        by more than 15 minutes. Early deliveries up to -15 min are expected
        (normal variance in generated data); anything beyond that threshold
        indicates a genuinely corrupted timestamp, not an early arrival.

2. Your design decisions doc / data quality log writeup — this is the story-worthy part. Something like:

A naive test for "delivery before scheduled time" would have flagged ~145K rows (15% of all deliveries) — but most of these are legitimate early deliveries, an artifact of how delivery timestamps were simulated (-15 to +90 minute random offset from scheduled time). Only 9,806 rows were deliberately corrupted (scheduled/actual times swapped). The test was refined to use a -15 minute threshold, isolating the actual data quality issue from expected variance and avoiding a ~93% false-positive rate.

That second version is the one worth keeping — it shows you caught a subtle false-positive problem before it shipped, not after. That's a much stronger portfolio line than "added dbt tests."
