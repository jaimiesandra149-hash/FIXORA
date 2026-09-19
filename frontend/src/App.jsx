import { useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const examples = [
  "My phone became very slow after the update",
  "My battery drains very quickly",
  "My screen flickers",
];

function App() {
  const [problem, setProblem] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [guidedSession, setGuidedSession] = useState(null);

  const analyzeProblem = async () => {
    if (!problem.trim()) return;

    setLoading(true);

    try {
      const response = await fetch(`${API}/troubleshoot`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          problem: problem.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);

      setResult({
        error: "Could not connect to FIXORA backend.",
      });
    } finally {
      setLoading(false);
    }
  };

  const startGuidedFix = async () => {
    setLoading(true);

    try {
      const response = await fetch(`${API}/troubleshoot/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          problem: problem.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start guided troubleshooting");
      }

      const data = await response.json();
      setGuidedSession(data);
    } catch (error) {
      console.error(error);
      alert("Could not start Guided Fix Mode.");
    } finally {
      setLoading(false);
    }
  };

  const completeStep = async () => {
    if (!guidedSession) return;

    setLoading(true);

    try {
      const response = await fetch(
        `${API}/troubleshoot/${guidedSession.session_id}/complete`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to complete step");
      }

      const data = await response.json();

      if (data.status === "completed") {
        setGuidedSession({
          ...guidedSession,
          completed: true,
          verification: data.verification,
        });
      } else {
        setGuidedSession({
          ...guidedSession,
          ...data,
        });
      }
    } catch (error) {
      console.error(error);
      alert("Could not continue the troubleshooting session.");
    } finally {
      setLoading(false);
    }
  };

  const resetApp = () => {
    setProblem("");
    setResult(null);
    setGuidedSession(null);
  };

  return (
    <div className="app">
      <nav className="navbar">
        <div className="logo">
          <span className="logo-mark">F</span>
          FIXORA
        </div>

        <div className="nav-status">
          <span className="status-dot"></span>
          Smart Troubleshooting Engine
        </div>
      </nav>

      <main className="main">

        {/* HOME */}
        {!result && !guidedSession && (
          <section className="hero">
            <div className="badge">
              SMART GUIDED TROUBLESHOOTING
            </div>

            <h1>
              Fix your device.
              <br />
              <span>One step at a time.</span>
            </h1>

            <p className="subtitle">
              Describe what's wrong with your Galaxy device in your own
              words. FIXORA turns your problem into a clear troubleshooting
              plan.
            </p>

            <div className="input-card">
              <label>What is happening with your device?</label>

              <textarea
                value={problem}
                maxLength={500}
                rows={4}
                placeholder='Try: "My phone became very slow after the update"'
                onChange={(e) => setProblem(e.target.value)}
              />

              <div className="input-bottom">
                <span>{problem.length}/500</span>

                <button
                  onClick={analyzeProblem}
                  disabled={!problem.trim() || loading}
                >
                  {loading ? "Analyzing..." : "Find a Fix →"}
                </button>
              </div>
            </div>

            <div className="examples">
              <span>Try an example:</span>

              {examples.map((example) => (
                <button
                  key={example}
                  onClick={() => setProblem(example)}
                >
                  {example}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* ANALYSIS */}
        {result && !guidedSession && (
          <section className="results">
            <button className="back-button" onClick={resetApp}>
              ← New problem
            </button>

            {result.error ? (
              <div className="verification-card error-card">
                <div className="check-icon">!</div>

                <div>
                  <h2>{result.error}</h2>
                  <p>
                    Make sure the FastAPI backend is running on port 8000.
                  </p>
                </div>
              </div>
            ) : (
              <>
                <div className="result-header">
                  <div className="badge">ANALYSIS COMPLETE</div>

                  <h1>We found a troubleshooting path.</h1>

                  <p>
                    FIXORA converted your natural-language complaint into
                    structured troubleshooting information.
                  </p>
                </div>

                {/* PROBLEM */}
                <div className="issue-card">
                  <div className="issue-main">
                    <span className="small-label">YOUR PROBLEM</span>

                    <h2>{result.problem}</h2>
                  </div>

                  <div className="category">
                    <span className="small-label">CATEGORY</span>

                    <strong>
                      {result.issue?.category || "General"}
                    </strong>
                  </div>
                </div>

                {/* ENRICHMENT */}
                <div className="enrichment-grid">
                  <div className="info-card">
                    <span className="small-label">DEVICE</span>
                    <h3>
                      {result.issue?.device || "Galaxy device"}
                    </h3>
                  </div>

                  <div className="info-card">
                    <span className="small-label">SYMPTOMS</span>
                    <h3>
                      {result.issue?.symptoms?.length
                        ? result.issue.symptoms.join(", ")
                        : "Not detected"}
                    </h3>
                  </div>

                  <div className="info-card">
                    <span className="small-label">TRIGGER</span>
                    <h3>
                      {result.issue?.triggers?.length
                        ? result.issue.triggers.join(", ")
                        : "Not detected"}
                    </h3>
                  </div>
                </div>

                {/* ACTIONS */}
                <div className="steps-section">
                  <div className="section-title">
                    <span>01</span>

                    <div>
                      <h2>Recommended actions</h2>
                      <p>
                        FIXORA orders safer troubleshooting actions first.
                      </p>
                    </div>
                  </div>

                  <div className="steps">
                    {(result.actions || []).map((action) => (
                      <div className="step-card" key={action.step}>
                        <div className="step-number">
                          {String(action.step).padStart(2, "0")}
                        </div>

                        <div className="step-content">
                          <h3>{action.title}</h3>

                          <p>
                            {action.type === "auto"
                              ? "Automatic / quick action"
                              : "Manual action"}
                          </p>
                        </div>

                        <div className="step-type">
                          {action.type}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* GUIDED FIX CTA */}
                <div className="verification-card">
                  <div className="check-icon">✓</div>

                  <div>
                    <h2>Ready to troubleshoot?</h2>

                    <p>
                      Follow the recommended actions one step at a time
                      with Guided Fix Mode.
                    </p>
                  </div>

                  <button
                    onClick={startGuidedFix}
                    disabled={loading}
                  >
                    {loading ? "Starting..." : "Start Guided Fix →"}
                  </button>
                </div>
              </>
            )}
          </section>
        )}

        {/* GUIDED FIX */}
        {guidedSession && (
          <section className="results">
            <button
              className="back-button"
              onClick={() => setGuidedSession(null)}
            >
              ← Back to troubleshooting plan
            </button>

            {!guidedSession.completed ? (
              <>
                <div className="result-header">
                  <div className="badge">GUIDED FIX MODE</div>

                  <h1>Let's fix it together.</h1>

                  <p>
                    Complete each step before moving to the next one.
                  </p>
                </div>

                <div className="guided-card">
                  <div className="guided-number">
                    {String(
                      guidedSession.progress?.current || 1
                    ).padStart(2, "0")}
                  </div>

                  <span className="small-label">
                    STEP {guidedSession.progress?.current || 1} OF{" "}
                    {guidedSession.progress?.total || 1}
                  </span>

                  <h2>
                    {guidedSession.current_action?.title}
                  </h2>

                  <div className="guided-type">
                    {guidedSession.current_action?.type}
                  </div>

                  <p className="guided-description">
                    Complete this action on your device, then continue
                    to the next troubleshooting step.
                  </p>

                  <button
                    className="complete-button"
                    onClick={completeStep}
                    disabled={loading}
                  >
                    {loading
                      ? "Updating..."
                      : "I've completed this step →"}
                  </button>

                  <div className="progress-bar">
                    <div
                      style={{
                        width: `${
                          ((guidedSession.progress?.current || 1) /
                            (guidedSession.progress?.total || 1)) *
                          100
                        }%`,
                      }}
                    ></div>
                  </div>
                </div>
              </>
            ) : (
              <div className="completion-card">
                <div className="completion-icon">✓</div>

                <div className="badge">TROUBLESHOOTING COMPLETE</div>

                <h1>You've completed the fix path.</h1>

                <p>
                  Is your Galaxy device working normally now?
                </p>

                <div className="completion-buttons">
                  <button onClick={resetApp}>
                    Yes, issue fixed
                  </button>

                  <button
                    onClick={() => {
                      setGuidedSession(null);
                    }}
                  >
                    No, issue continues
                  </button>
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      <footer>
        <span>FIXORA</span>
        <span>Smart Guided Troubleshooting Engine</span>
      </footer>
    </div>
  );
}

export default App;