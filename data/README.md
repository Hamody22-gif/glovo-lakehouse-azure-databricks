# data/

Local working folder for the dataset. Its contents are ignored by Git.

Download `glovo_parquet.zip` from the repository's Releases page and unzip it into
`data/landing/`. To rebuild the Parquet files from the original CSVs:

```bash
python tools/csv_to_parquet.py data/raw_csv data/landing
```
