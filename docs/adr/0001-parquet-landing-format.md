# ADR-0001: Parquet as the landing format, messy columns kept as text

- **Status:** Accepted
- **Date:** 2026-11-17

## Context

The source dataset arrived as 10 CSV files (~23 MB). CSV has no schema, no compression and
is easy to corrupt: the orders file had been opened and re-saved in Excel, which rewrote
most timestamps to US `M/D/YYYY H:MM` format, dropped seconds and most likely swapped day
and month on `DD/MM/YYYY` values whose day was 12 or less.

## Decision

Convert every CSV to Parquet (snappy compression) with `tools/csv_to_parquet.py`:

1. Read every column as text first, so nothing is silently reinterpreted.
2. Turn empty strings into nulls.
3. Give a column a real type (int64, double, date, boolean) only if **all** its non-null
   values cast cleanly.
4. Keep columns whose problem is their *format* as strings on purpose:
   `menu_items.price_pln`, `payments.payment_value_pln` and the three order timestamps.
   Parsing them is the Silver layer's job, where bad values can be quarantined and counted.

## Consequences

- Files shrink from ~23 MB to ~12 MB and carry a schema.
- Bad *values* (negative quantities, 9999 km distances, review scores of 10) are still
  present for Silver expectations to catch.
- Bronze must not cast the text columns; Silver owns all parsing.
- The Excel damage to order timestamps is recorded as a known issue. Silver rule:
  slash timestamps **with** seconds are `DD/MM/YYYY`, **without** seconds are `M/D/YYYY`;
  rows where delivery precedes placement are quarantined.
- In production, raw data often arrives as CSV or JSON; the Bronze loader should be able
  to ingest both formats.
