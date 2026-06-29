import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { runResearch } from "./api";
import "./App.css";

const AGENT_STEPS = [
  { key: "research", label: "Researcher", action: "drafting" },
  { key: "factcheck", label: "Fact Checker", action: "verifying" },
  { key: "write", label: "Writer", action: "composing" },
  { key: "critique", label: "Critic", action: "reviewing" },
];

function App() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runResearch(topic);
      setResult(data);
    } catch (err) {
      setError("The pipeline could not complete. Try a different topic, or try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header className="masthead">
        <p className="masthead-label">A multi-agent editorial process</p>
        <h1>The Research Desk</h1>
        <p className="masthead-sub">
          Four AI specialists draft, verify, compose, and review every submission.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="submission">
        <label htmlFor="topic">Submit a topic for review</label>
        <div className="submission-row">
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. the future of carbon capture"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !topic.trim()}>
            {loading ? "In review" : "Submit"}
          </button>
        </div>
      </form>

      {(loading || result) && (
        <ol className="trail">
          {AGENT_STEPS.map((step, i) => (
            <li key={step.key} className={loading ? "active" : "done"}>
              <span className="trail-mark">{loading ? "·" : "✓"}</span>
              <span className="trail-label">{step.label}</span>
              <span className="trail-action">
                {loading ? step.action : "complete"}
              </span>
            </li>
          ))}
        </ol>
      )}

      {error && (
        <div className="notice notice-error">
          <p className="notice-label">Returned unread</p>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <article className="manuscript">
          {result.summary && (
            <section>
              <p className="byline">Researcher's brief</p>
              <p className="lede">{result.summary}</p>
            </section>
          )}

          {result.key_facts && (
            <section>
              <p className="byline">Findings on record</p>
              <ul className="findings">
                {result.key_facts.map((fact, i) => (
                  <li key={i}>{fact}</li>
                ))}
              </ul>
            </section>
          )}

          {result.report_markdown && (
            <section className="full-report">
              <p className="byline">Final draft</p>
              <ReactMarkdown>{result.report_markdown}</ReactMarkdown>
            </section>
          )}

          {result.score !== undefined && (
            <footer className="margin-note">
              <span className="margin-mark">{result.score}/10</span>
              <span className="margin-text">
                {result.verdict === "approved"
                  ? "Approved by the critic"
                  : "Returned for revision"}
              </span>
            </footer>
          )}
        </article>
      )}
    </div>
  );
}

export default App;