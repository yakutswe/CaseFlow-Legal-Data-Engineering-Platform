import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  BookOpen,
  Database,
  FileSearch,
  Scale,
  Search,
  ShieldCheck,
  Sparkles
} from "lucide-react";

type SearchResult = {
  case_id: number;
  case_name: string;
  decision_date: string | null;
  source_url: string;
  rank: number;
  snippet: string;
};

type TopCitation = {
  cited_case_name: string;
  citation_count: number;
};

type Citation = {
  id: number;
  citing_case_id: number;
  cited_case_name: string | null;
  volume: number;
  reporter: string;
  page: number;
  pin_cite: number | null;
  year: number | null;
};

function cleanSnippet(value: string) {
  return value
    .replaceAll("<mark>", "<strong>")
    .replaceAll("</mark>", "</strong>");
}

export default function App() {
  const [query, setQuery] = useState("standing");
  const [submittedQuery, setSubmittedQuery] = useState("standing");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [topCitations, setTopCitations] = useState<TopCitation[]>([]);
  const [selected, setSelected] = useState<SearchResult | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  async function runSearch(q: string) {
    setLoading(true);
    try {
      const response = await fetch(`/search?q=${encodeURIComponent(q)}&limit=8&offset=0`);
      if (!response.ok) throw new Error("Search request failed");
      const data = (await response.json()) as SearchResult[];
      setResults(data);
      if (data.length && !selected) setSelected(data[0]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetch("/health")
      .then((r) => {
        setHealthy(r.ok);
        return r.json();
      })
      .catch(() => setHealthy(false));

    fetch("/citations/top?limit=6")
      .then((r) => r.json())
      .then((data: TopCitation[]) => setTopCitations(data))
      .catch(() => setTopCitations([]));

    runSearch(submittedQuery);
  }, []);

  useEffect(() => {
    if (!selected) {
      setCitations([]);
      return;
    }

    fetch(`/cases/${selected.case_id}/citations`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data: Citation[]) => setCitations(data))
      .catch(() => setCitations([]));
  }, [selected]);

  const maxCitation = useMemo(
    () => Math.max(1, ...topCitations.map((item) => item.citation_count)),
    [topCitations]
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    const value = query.trim();
    if (!value) return;
    setSubmittedQuery(value);
    setSelected(null);
    runSearch(value);
  }

  return (
    <div className="app-shell">
      <header className="nav">
        <div className="container nav-inner">
          <a className="brand" href="#">
            <div className="brand-mark"><Scale size={18} /></div>
            <span>CaseFlow</span>
          </a>
          <nav className="nav-links">
            <a href="#search">Search</a>
            <a href="#citations">Citations</a>
            <a href="http://127.0.0.1:8000/docs" target="_blank">API Docs</a>
          </nav>
          <div className={`status ${healthy === false ? "offline" : ""}`}>
            <span className="status-dot" />
            {healthy === null ? "Checking" : healthy ? "System healthy" : "Offline"}
          </div>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="container">
            <div className="eyebrow"><Sparkles size={14} /> Legal intelligence platform</div>
            <h1>Search opinions.<br />Understand citations.</h1>
            <p className="hero-copy">
              CaseFlow turns raw court opinions into searchable, connected legal intelligence —
              with ranked full-text search, citation extraction, source traceability, and resilient ingestion.
            </p>

            <form className="search-box" onSubmit={submit} id="search">
              <Search size={20} />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search opinions, doctrine, or legal concepts"
                aria-label="Search legal opinions"
              />
              <button type="submit">Search</button>
            </form>

            <div className="quick-row">
              <span>Try:</span>
              {["standing", "irreparable harm", "election", "injunction"].map((term) => (
                <button
                  key={term}
                  onClick={() => {
                    setQuery(term);
                    setSubmittedQuery(term);
                    setSelected(null);
                    runSearch(term);
                  }}
                >
                  {term}
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="container metrics">
          <div className="metric-card">
            <div className="metric-icon"><FileSearch size={19} /></div>
            <div><span className="metric-value">{results.length}</span><span className="metric-label">Top matches</span></div>
          </div>
          <div className="metric-card">
            <div className="metric-icon"><BookOpen size={19} /></div>
            <div><span className="metric-value">{topCitations.length}</span><span className="metric-label">Citation leaders</span></div>
          </div>
          <div className="metric-card">
            <div className="metric-icon"><Database size={19} /></div>
            <div><span className="metric-value">Postgres</span><span className="metric-label">GIN full-text index</span></div>
          </div>
          <div className="metric-card">
            <div className="metric-icon"><ShieldCheck size={19} /></div>
            <div><span className="metric-value">7/7</span><span className="metric-label">Core tests passing</span></div>
          </div>
        </section>

        <section className="container workspace">
          <div className="results-panel">
            <div className="section-heading">
              <div>
                <span className="section-kicker">Search results</span>
                <h2>“{submittedQuery}”</h2>
              </div>
              <span className="result-count">{loading ? "Searching…" : `${results.length} shown`}</span>
            </div>

            <div className="result-list">
              {results.map((item) => (
                <button
                  key={item.case_id}
                  className={`result-card ${selected?.case_id === item.case_id ? "active" : ""}`}
                  onClick={() => setSelected(item)}
                >
                  <div className="result-topline">
                    <span className="case-name">{item.case_name}</span>
                    <span className="rank">rank {item.rank.toFixed(3)}</span>
                  </div>
                  <div className="meta">
                    {item.decision_date || "Decision date unavailable"} · Case #{item.case_id}
                  </div>
                  <p
                    className="snippet"
                    dangerouslySetInnerHTML={{ __html: cleanSnippet(item.snippet) }}
                  />
                </button>
              ))}

              {!loading && results.length === 0 && (
                <div className="empty-state">No matching opinions found.</div>
              )}
            </div>
          </div>

          <aside className="detail-panel">
            {selected ? (
              <>
                <span className="section-kicker">Selected case</span>
                <h3>{selected.case_name}</h3>
                <div className="detail-meta">
                  <span>Case #{selected.case_id}</span>
                  <span>{selected.decision_date || "Date unavailable"}</span>
                </div>
                <a className="source-link" href={selected.source_url} target="_blank">
                  Open source opinion <ArrowUpRight size={15} />
                </a>

                <div className="divider" />

                <div className="detail-title">
                  <span>Citations extracted</span>
                  <strong>{citations.length}</strong>
                </div>

                <div className="citation-list">
                  {citations.slice(0, 8).map((citation) => (
                    <div className="citation-row" key={citation.id}>
                      <div>
                        <strong>
                          {citation.cited_case_name ||
                            `${citation.volume} ${citation.reporter} ${citation.page}`}
                        </strong>
                        <span>
                          {citation.volume} {citation.reporter} {citation.page}
                          {citation.year ? ` (${citation.year})` : ""}
                        </span>
                      </div>
                    </div>
                  ))}
                  {!citations.length && <div className="small-empty">No extracted citations for this case.</div>}
                </div>
              </>
            ) : (
              <div className="detail-placeholder">
                <Scale size={28} />
                <p>Select a search result to inspect its citation intelligence.</p>
              </div>
            )}
          </aside>
        </section>

        <section className="citation-section" id="citations">
          <div className="container citation-grid">
            <div>
              <span className="section-kicker">Citation intelligence</span>
              <h2>Most referenced authorities</h2>
              <p>
                Structured citations are extracted from opinion text and aggregated to reveal frequently
                referenced authorities across the corpus.
              </p>
            </div>

            <div className="leaderboard">
              {topCitations.map((item, index) => (
                <div className="leader-row" key={`${item.cited_case_name}-${index}`}>
                  <span className="leader-index">{String(index + 1).padStart(2, "0")}</span>
                  <div className="leader-main">
                    <div className="leader-label">
                      <strong>{item.cited_case_name}</strong>
                      <span>{item.citation_count}</span>
                    </div>
                    <div className="bar">
                      <span style={{ width: `${(item.citation_count / maxCitation) * 100}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="container architecture">
          <div className="architecture-copy">
            <span className="section-kicker">Built for traceability</span>
            <h2>From source document to searchable intelligence.</h2>
          </div>
          <div className="architecture-flow">
            {[
              ["01", "Ingest", "Official court sources"],
              ["02", "Parse", "PDF text + metadata"],
              ["03", "Normalize", "Hash + deduplicate"],
              ["04", "Index", "PostgreSQL full-text"],
              ["05", "Connect", "Citation graph"],
              ["06", "Serve", "FastAPI + dashboard"]
            ].map(([num, title, description]) => (
              <div className="flow-step" key={num}>
                <span>{num}</span>
                <strong>{title}</strong>
                <small>{description}</small>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer>
        <div className="container footer-inner">
          <div>
            <strong>CaseFlow</strong>
            <span>Legal data ingestion and citation intelligence platform</span>
          </div>
          <span>FastAPI · PostgreSQL · Docker · Python</span>
        </div>
      </footer>
    </div>
  );
}
