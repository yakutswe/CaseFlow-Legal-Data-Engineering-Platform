from ingestion.sources.courtlistener_source import CourtListenerSource


source = CourtListenerSource(
    query="Miranda v Arizona",
)

records = source.fetch()

print(f"Fetched: {len(records)}")

for record in records[:3]:
    print(record)