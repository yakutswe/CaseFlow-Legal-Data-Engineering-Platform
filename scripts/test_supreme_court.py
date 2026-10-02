from ingestion.sources.supreme_court_source import SupremeCourtSource


source = SupremeCourtSource()

records = source.fetch()

print(f"Fetched {len(records)} records")

for record in records[:5]:
    print(record)