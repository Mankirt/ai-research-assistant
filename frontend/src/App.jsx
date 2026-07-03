import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { startResearch, checkStatus } from "./api";
import "./App.css";

const AGENT_STEPS = [
  { key: "cache_check", label: "Cache Check", action: "checking cache" },
  { key: "research", label: "Researcher", action: "drafting" },
  { key: "factcheck", label: "Fact Checker", action: "verifying" },
  { key: "write", label: "Writer", action: "composing" },
  { key: "critique", label: "Critic", action: "reviewing" },
];

function getStepState(stepKey, currentStep, status) {
  if (status === "SUCCEEDED") return "done";
  if (!currentStep) return "pending";

  const currentIndex = AGENT_STEPS.findIndex((s) => s.key === currentStep);
  const stepIndex = AGENT_STEPS.findIndex((s) => s.key === stepKey);

  if (stepIndex < currentIndex) return "done";
  if (stepIndex === currentIndex) return "active";
  return "pending";
}

function App() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setCurrentStep(null);

    try {
      const executionArn = await startResearch(topic);

      pollRef.current = setInterval(async () => {
        try {
          const statusData = await checkStatus(executionArn);

          if (statusData.status === "RUNNING") {
            setCurrentStep(statusData.current_step);
          } else if (statusData.status === "SUCCEEDED") {
            clearInterval(pollRef.current);
            setCurrentStep(null);
            const finalResult = statusData.result?.body
              ? JSON.parse(statusData.result.body)
              : statusData.result;
            setResult(finalResult);
            setLoading(false);
          } else if (statusData.status === "FAILED") {
            clearInterval(pollRef.current);
            setError("The research pipeline failed. Please try again.");
            setLoading(false);
          }
        } catch (err) {
          clearInterval(pollRef.current);
          setError("Lost connection to the pipeline. Please try again.");
          setLoading(false);
        }
      }, 2000);

    } catch (err) {
      setError("Failed to start research. Please try again.");
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
          {AGENT_STEPS.map((step) => {
            const state = getStepState(
              step.key,
              currentStep,
              result ? "SUCCEEDED" : "RUNNING"
            );
            return (
              <li key={step.key} className={state}>
                <span className="trail-mark">
                  {state === "done" ? "✓" : state === "active" ? "·" : "○"}
                </span>
                <span className="trail-label">{step.label}</span>
                <span className="trail-action">
                  {state === "done"
                    ? "complete"
                    : state === "active"
                    ? step.action
                    : "waiting"}
                </span>
              </li>
            );
          })}
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

          {result.suggested_improvements &&
            result.suggested_improvements.length > 0 && (
              <section>
                <p className="byline">Ways to go deeper</p>
                <ul className="findings">
                  {result.suggested_improvements.map((suggestion, i) => (
                    <li key={i}>{suggestion}</li>
                  ))}
                </ul>
              </section>
            )}

          {result.critique_summary && (
            <footer className="margin-note">
              <span className="margin-text">{result.critique_summary}</span>
            </footer>
          )}
        </article>
      )}
    </div>
  );
}

export default App;