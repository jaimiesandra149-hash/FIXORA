import { useState, useEffect } from "react";
import {
  Zap,
  BatteryCharging,
  Wifi,
  Smartphone,
  Plug,
  Flame,
  Volume2,
  Camera,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  Copy,
  Check,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Clock,
  ChevronRight,
  HelpCircle,
  Wrench,
  LifeBuoy
} from "lucide-react";
import "./App.css";

// Support both direct URL and relative Vite proxy
const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const QUICK_CATEGORIES = [
  {
    id: "battery",
    label: "Battery Drain",
    icon: BatteryCharging,
    sample: "My battery drains extremely fast and gets warm even on standby after the latest update."
  },
  {
    id: "performance",
    label: "Lag & Slowdown",
    icon: Zap,
    sample: "Phone is lagging, freezing when switching apps, and keyboard takes 2 seconds to appear."
  },
  {
    id: "connectivity",
    label: "Wi-Fi & Bluetooth",
    icon: Wifi,
    sample: "Wi-Fi keeps disconnecting randomly every few minutes and Bluetooth audio cuts out."
  },
  {
    id: "display",
    label: "Screen & Touch",
    icon: Smartphone,
    sample: "Screen flickers occasionally at low brightness and touches register incorrectly."
  },
  {
    id: "charging",
    label: "Charging / Moisture",
    icon: Plug,
    sample: "Phone shows 'Moisture detected in USB port' warning and will not charge with cable."
  },
  {
    id: "overheating",
    label: "Overheating",
    icon: Flame,
    sample: "Device gets burning hot near the camera while charging or playing games."
  },
  {
    id: "audio",
    label: "Sound & Mic",
    icon: Volume2,
    sample: "No sound from bottom speaker during media playback and callers say my mic is muffled."
  },
  {
    id: "camera",
    label: "Camera Glitch",
    icon: Camera,
    sample: "Camera app shows 'Warning: Camera Failed' when opened or pictures come out blurry."
  }
];

const DEVICE_PRESETS = [
  "Galaxy S24 / S24 Ultra",
  "Galaxy S23 / S22 Series",
  "Galaxy Z Fold / Flip",
  "Galaxy A-Series (A54/A55)",
  "Galaxy Tab",
  "Other Galaxy Device"
];

function App() {
  const [problem, setProblem] = useState("");
  const [deviceModel, setDeviceModel] = useState("Galaxy S24 / S24 Ultra");
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [result, setResult] = useState(null);
  const [guidedSession, setGuidedSession] = useState(null);
  const [copiedKey, setCopiedKey] = useState(null);
  const [checkedItems, setCheckedItems] = useState({});
  const [unresolvedEscalation, setUnresolvedEscalation] = useState(false);

  const checkBackendHealth = async () => {
    try {
      const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(3500) });
      if (res.ok) {
        setBackendStatus("online");
      } else {
        setBackendStatus("error");
      }
    } catch {
      try {
        const res2 = await fetch(`${API}/`, { signal: AbortSignal.timeout(2500) });
        if (res2.ok) setBackendStatus("online");
        else setBackendStatus("offline");
      } catch {
        setBackendStatus("offline");
      }
    }
  };

  // Check backend health on mount
  useEffect(() => {
    let ignore = false;
    async function verify() {
      try {
        const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(3500) });
        if (!ignore) setBackendStatus(res.ok ? "online" : "error");
      } catch {
        try {
          const res2 = await fetch(`${API}/`, { signal: AbortSignal.timeout(2500) });
          if (!ignore) setBackendStatus(res2.ok ? "online" : "offline");
        } catch {
          if (!ignore) setBackendStatus("offline");
        }
      }
    }
    verify();
    return () => { ignore = true; };
  }, []);

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleCategorySelect = (item) => {
    setProblem(item.sample);
  };

  const toggleInstructionCheck = (stepIdx, instrIdx) => {
    const key = `${stepIdx}-${instrIdx}`;
    setCheckedItems((prev) => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const analyzeProblem = async () => {
    if (!problem.trim()) return;
    setLoading(true);
    setUnresolvedEscalation(false);

    try {
      const response = await fetch(`${API}/troubleshoot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          problem: problem.trim(),
          device_model: deviceModel
        }),
      });

      if (!response.ok) throw new Error("Diagnostic request failed");

      const data = await response.json();
      setResult(data);
      setCheckedItems({});
    } catch (error) {
      console.error(error);
      setResult({
        error: "Unable to reach FIXORA Troubleshooting API. Verify the FastAPI server is running.",
      });
    } finally {
      setLoading(false);
    }
  };

  const startGuidedFix = async () => {
    setLoading(true);
    setUnresolvedEscalation(false);

    try {
      const response = await fetch(`${API}/troubleshoot/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          problem: problem.trim(),
          device_model: deviceModel
        }),
      });

      if (!response.ok) throw new Error("Failed to start guided session");

      const data = await response.json();
      setGuidedSession(data);
      setCheckedItems({});
    } catch (error) {
      console.error(error);
      alert("Could not start Guided Fix Mode. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const updateGuidedStep = async (action = "next", feedback = null) => {
    if (!guidedSession) return;
    setLoading(true);

    try {
      const response = await fetch(`${API}/troubleshoot/${guidedSession.session_id}/step`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, feedback }),
      });

      if (!response.ok) {
        // Fallback to legacy endpoint if available
        const legRes = await fetch(`${API}/troubleshoot/${guidedSession.session_id}/complete`, {
          method: "POST"
        });
        if (!legRes.ok) throw new Error("Step progression failed");
        const legData = await legRes.json();
        setGuidedSession((prev) => ({
          ...prev,
          ...legData,
          completed: legData.status === "completed"
        }));
        return;
      }

      const data = await response.json();
      if (data.status === "completed") {
        setGuidedSession((prev) => ({
          ...prev,
          completed: true,
          verification: data.verification,
          history: data.history || []
        }));
      } else {
        setGuidedSession((prev) => ({
          ...prev,
          ...data,
          completed: false
        }));
      }
      setCheckedItems({});
    } catch (error) {
      console.error(error);
      alert("Failed to advance guided troubleshooting step.");
    } finally {
      setLoading(false);
    }
  };

  const resetGuidedSession = async () => {
    if (!guidedSession) return;
    setLoading(true);
    try {
      const response = await fetch(`${API}/troubleshoot/${guidedSession.session_id}/reset`, {
        method: "POST"
      });
      if (response.ok) {
        const data = await response.json();
        setGuidedSession((prev) => ({
          ...prev,
          ...data,
          completed: false
        }));
        setCheckedItems({});
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const resetApp = () => {
    setProblem("");
    setResult(null);
    setGuidedSession(null);
    setCheckedItems({});
    setUnresolvedEscalation(false);
  };

  const copyDiagnosticReport = () => {
    if (!result) return;
    const report = [
      `=== FIXORA DIAGNOSTIC REPORT ===`,
      `Device: ${result.issue?.device || deviceModel}`,
      `Category: ${result.issue?.category?.toUpperCase() || "GENERAL"}`,
      `Fixability: ${result.issue?.fixability || "Standard"}`,
      `Symptoms: ${result.issue?.symptoms?.join(", ") || "None"}`,
      `Triggers: ${result.issue?.triggers?.join(", ") || "None"}`,
      `Severity: ${result.issue?.severity || "Standard"}`,
      `----------------------------------------`,
      `RECOMMENDED ACTION PLAN:`,
      ...(result.actions || []).map(
        (a) =>
          `[Step ${a.step}] ${a.title} (${a.estimated_time || "1m"})\nPath: ${a.settings_path || "N/A"}\nTip: ${a.tip || "N/A"}`
      ),
      `========================================`
    ].join("\n\n");

    copyToClipboard(report, "report");
  };

  return (
    <div className="app">
      {/* HEADER / NAVIGATION */}
      <nav className="navbar">
        <div className="logo-container" onClick={resetApp} role="button" tabIndex={0}>
          <div className="logo-mark">F</div>
          <div className="logo-text">
            <span className="brand-name">FIXORA</span>
            <span className="brand-tagline">AI Troubleshooting Engine</span>
          </div>
        </div>

        <div className="nav-controls">
          <div className={`status-pill ${backendStatus}`} onClick={checkBackendHealth} title="Click to refresh connection">
            <span className="status-indicator"></span>
            <span>
              {backendStatus === "online" && "Engine Online"}
              {backendStatus === "offline" && "Backend Offline (Click to Retry)"}
              {backendStatus === "checking" && "Connecting..."}
              {backendStatus === "error" && "API Warning"}
            </span>
          </div>

          {(result || guidedSession) && (
            <button className="nav-new-btn" onClick={resetApp}>
              <RotateCcw size={14} />
              <span>New Diagnostic</span>
            </button>
          )}
        </div>
      </nav>

      {/* MAIN CONTAINER */}
      <main className="main">
        {/* VIEW 1: HOME / ISSUE INPUT */}
        {!result && !guidedSession && (
          <section className="hero-section">
            <div className="badge-pill">
              <Sparkles size={13} className="badge-icon" />
              <span>SMART GUIDED TROUBLESHOOTING ENGINE 2.0</span>
            </div>

            <h1 className="hero-headline">
              Fix your device.
              <br />
              <span className="gradient-text">One precise step at a time.</span>
            </h1>

            <p className="hero-subtitle">
              Describe the glitch, lag, or battery symptom in everyday words. FIXORA converts your complaint
              into a verified, non-destructive step-by-step resolution plan.
            </p>

            {/* DEVICE SELECTOR ROW */}
            <div className="device-selector-wrapper">
              <label className="input-field-label">
                <Smartphone size={15} />
                <span>Target Galaxy Model:</span>
              </label>
              <div className="device-pills">
                {DEVICE_PRESETS.map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    className={`device-pill ${deviceModel === preset ? "active" : ""}`}
                    onClick={() => setDeviceModel(preset)}
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>

            {/* PROBLEM INPUT CARD */}
            <div className="input-card">
              <div className="input-card-header">
                <label htmlFor="problem-input" className="input-field-label">
                  <Wrench size={15} />
                  <span>Describe what is happening with your device:</span>
                </label>
                {problem.length > 0 && (
                  <button className="clear-btn" onClick={() => setProblem("")} type="button">
                    Clear
                  </button>
                )}
              </div>

              <textarea
                id="problem-input"
                value={problem}
                maxLength={800}
                rows={4}
                placeholder='e.g., "My battery has been draining from 80% to 15% in 3 hours after updating One UI, and the phone feels warm near the camera."'
                onChange={(e) => setProblem(e.target.value)}
                onKeyDown={(e) => {
                  if (e.ctrlKey && e.key === "Enter") analyzeProblem();
                }}
              />

              <div className="input-bottom-bar">
                <div className="char-count">
                  <span>{problem.length}</span>/800 chars
                  <span className="hint-text">• Press Ctrl + Enter to analyze</span>
                </div>

                <button
                  className="analyze-cta-btn"
                  onClick={analyzeProblem}
                  disabled={!problem.trim() || loading}
                >
                  {loading ? (
                    <>
                      <RefreshCw size={16} className="spin-icon" />
                      <span>Diagnosing Issue...</span>
                    </>
                  ) : (
                    <>
                      <span>Generate Fix Plan</span>
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* QUICK CATEGORY CHIPS */}
            <div className="quick-categories-section">
              <span className="quick-label">Or explore common issues:</span>
              <div className="category-chip-grid">
                {QUICK_CATEGORIES.map((cat) => {
                  const Icon = cat.icon;
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      className="category-chip"
                      onClick={() => handleCategorySelect(cat)}
                    >
                      <Icon size={14} className="chip-icon" />
                      <span>{cat.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* VIEW 2: DIAGNOSTIC ANALYSIS & STEP PLAN */}
        {result && !guidedSession && (
          <section className="results-container">
            <div className="result-top-nav">
              <button className="back-link-btn" onClick={resetApp}>
                <ArrowLeft size={16} />
                <span>Change Problem Description</span>
              </button>

              {!result.error && (
                <button className="secondary-action-btn" onClick={copyDiagnosticReport}>
                  {copiedKey === "report" ? <Check size={14} /> : <Copy size={14} />}
                  <span>{copiedKey === "report" ? "Report Copied!" : "Export Diagnostic Report"}</span>
                </button>
              )}
            </div>

            {result.error ? (
              <div className="alert-card error-alert">
                <div className="alert-icon-box danger">
                  <AlertTriangle size={24} />
                </div>
                <div>
                  <h3>Diagnostic Service Error</h3>
                  <p>{result.error}</p>
                  <p className="alert-subtext">
                    Ensure the FastAPI server is running with <code>uvicorn app:app --reload --port 8000</code>.
                  </p>
                  <button className="retry-btn" onClick={analyzeProblem}>
                    <RefreshCw size={14} /> Retry Request
                  </button>
                </div>
              </div>
            ) : (
              <>
                {/* SUMMARY BANNER */}
                <div className="diagnostic-summary-card">
                  <div className="summary-left">
                    <div className="badge-pill small">
                      <ShieldCheck size={13} />
                      <span>ANALYSIS COMPLETE • {result.summary?.total_steps || result.actions?.length || 0} VERIFIED STEPS</span>
                    </div>

                    <h2 className="summary-title">{result.issue?.category ? `${result.issue.category.toUpperCase()} DIAGNOSTIC` : "DEVICE DIAGNOSTIC"}</h2>
                    <p className="summary-desc">
                      Root problem: <em>"{result.problem}"</em>
                    </p>

                    <div className="tags-row">
                      <span className="meta-tag device-tag">
                        <Smartphone size={12} />
                        {result.issue?.device || deviceModel}
                      </span>
                      <span className={`meta-tag severity-tag ${result.issue?.severity?.toLowerCase() || "standard"}`}>
                        Severity: {result.issue?.severity || "Standard"}
                      </span>
                      <span className="meta-tag fixability-tag">
                        {result.issue?.fixability || "Software Fixable"}
                      </span>
                      {result.summary?.estimated_duration && (
                        <span className="meta-tag time-tag">
                          <Clock size={12} />
                          Est. Time: {result.summary.estimated_duration}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="summary-right">
                    <button className="start-guided-primary-btn" onClick={startGuidedFix} disabled={loading}>
                      <span>Start Guided Fix Mode</span>
                      <ArrowRight size={18} />
                    </button>
                    <span className="sub-cta-note">Interactive step-by-step walkthrough</span>
                  </div>
                </div>

                {/* HARDWARE WARNING ALERT (IF APPLICABLE) */}
                {result.issue?.hardware_risk && (
                  <div className="alert-card hardware-warning">
                    <div className="alert-icon-box warning">
                      <AlertTriangle size={24} />
                    </div>
                    <div>
                      <h4>Physical Hardware Advisory</h4>
                      <p>
                        Some symptoms in your report suggest potential physical wear, panel pressure, or internal moisture.
                        Try the software steps first, but avoid forced charging or third-party repair tools if physical damage is present.
                      </p>
                    </div>
                  </div>
                )}

                {/* SYMPTOMS & TRIGGERS METRIC TILES */}
                <div className="metrics-grid">
                  <div className="metric-tile">
                    <span className="tile-label">DETECTED SYMPTOMS</span>
                    <p className="tile-value">
                      {result.issue?.symptoms?.length ? result.issue.symptoms.join(" • ") : "General malfunction"}
                    </p>
                  </div>
                  <div className="metric-tile">
                    <span className="tile-label">POTENTIAL TRIGGER</span>
                    <p className="tile-value">
                      {result.issue?.triggers?.length ? result.issue.triggers.join(" • ") : "Standard background operation"}
                    </p>
                  </div>
                  <div className="metric-tile">
                    <span className="tile-label">DIAGNOSTIC CONFIDENCE</span>
                    <p className="tile-value highlight">
                      {result.issue?.confidence ? `${result.issue.confidence}% match` : "95% match"}
                    </p>
                  </div>
                </div>

                {/* STEP-BY-STEP ACTION CARDS */}
                <div className="action-plan-section">
                  <div className="plan-header">
                    <div>
                      <h3 className="section-heading">Recommended Troubleshooting Plan</h3>
                      <p className="section-subheading">
                        Safest and non-destructive resolutions are prioritized first to protect your personal files.
                      </p>
                    </div>

                    <button className="launch-guided-btn" onClick={startGuidedFix}>
                      <Wrench size={14} />
                      <span>Follow Steps Interactively</span>
                    </button>
                  </div>

                  <div className="step-cards-list">
                    {(result.actions || []).map((action, idx) => (
                      <div className="full-step-card" key={action.step || idx}>
                        <div className="step-card-side">
                          <div className="step-badge-number">
                            {String(action.step || idx + 1).padStart(2, "0")}
                          </div>
                          <span className="step-est-time">
                            <Clock size={11} />
                            {action.estimated_time || "1m"}
                          </span>
                        </div>

                        <div className="step-card-body">
                          <div className="step-title-row">
                            <h4 className="step-title">{action.title}</h4>
                            <div className="step-badges">
                              <span className={`safety-badge ${action.safety_level?.toLowerCase().includes("reset") ? "caution" : "safe"}`}>
                                <ShieldCheck size={12} />
                                {action.safety_level || "Safe"}
                              </span>
                              <span className="type-badge">{action.type || "Manual"}</span>
                            </div>
                          </div>

                          <p className="step-description">{action.description}</p>

                          {/* SETTINGS PATHWAY */}
                          {action.settings_path && (
                            <div className="settings-breadcrumb-box">
                              <span className="breadcrumb-label">Device Path:</span>
                              <code className="breadcrumb-code">{action.settings_path}</code>
                              <button
                                className="copy-breadcrumb-btn"
                                onClick={() => copyToClipboard(action.settings_path, `path-${idx}`)}
                                title="Copy pathway"
                              >
                                {copiedKey === `path-${idx}` ? <Check size={12} /> : <Copy size={12} />}
                              </button>
                            </div>
                          )}

                          {/* INSTRUCTIONS */}
                          {action.instructions && action.instructions.length > 0 && (
                            <div className="step-checklist">
                              <span className="checklist-heading">How to execute this step:</span>
                              <ul>
                                {action.instructions.map((inst, iIdx) => (
                                  <li key={iIdx}>{inst}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* PRO TIP */}
                          {action.tip && (
                            <div className="step-tip-box">
                              <Sparkles size={14} className="tip-sparkle" />
                              <div>
                                <strong>Pro-Tip: </strong>
                                <span>{action.tip}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* BOTTOM CTA */}
                <div className="bottom-guided-prompt">
                  <div className="guided-prompt-content">
                    <LifeBuoy size={28} className="prompt-icon" />
                    <div>
                      <h4>Ready to execute these steps?</h4>
                      <p>Guided Fix Mode walks you through each step on your Galaxy phone with real-time feedback.</p>
                    </div>
                  </div>
                  <button className="start-guided-primary-btn" onClick={startGuidedFix}>
                    <span>Launch Guided Fix</span>
                    <ChevronRight size={16} />
                  </button>
                </div>
              </>
            )}
          </section>
        )}

        {/* VIEW 3: INTERACTIVE GUIDED FIX MODE */}
        {guidedSession && (
          <section className="guided-mode-container">
            <div className="guided-top-bar">
              <button className="back-link-btn" onClick={() => setGuidedSession(null)}>
                <ArrowLeft size={16} />
                <span>Return to Plan Overview</span>
              </button>

              <div className="guided-header-info">
                <span className="guided-mode-tag">
                  <Wrench size={13} />
                  GUIDED FIX MODE
                </span>
                <span className="guided-session-id">Session #{guidedSession.session_id}</span>
              </div>
            </div>

            {!guidedSession.completed && !unresolvedEscalation ? (
              <div className="guided-step-frame">
                {/* PROGRESS TRACKER */}
                <div className="guided-progress-header">
                  <div className="progress-text-row">
                    <span className="step-counter-text">
                      Step <strong>{guidedSession.progress?.current || 1}</strong> of{" "}
                      <strong>{guidedSession.progress?.total || 1}</strong>
                    </span>
                    <span className="percent-text">{guidedSession.progress?.percent || 25}% Completed</span>
                  </div>

                  <div className="progress-bar-track">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${guidedSession.progress?.percent || ((guidedSession.progress?.current || 1) / (guidedSession.progress?.total || 1)) * 100}%`
                      }}
                    ></div>
                  </div>

                  {/* STEP TABS */}
                  {guidedSession.all_actions && (
                    <div className="stepper-dots-bar">
                      {guidedSession.all_actions.map((act, aIdx) => {
                        const isDone = aIdx + 1 < (guidedSession.progress?.current || 1);
                        const isCurrent = aIdx + 1 === (guidedSession.progress?.current || 1);
                        return (
                          <div
                            key={act.step || aIdx}
                            className={`stepper-pill ${isDone ? "done" : ""} ${isCurrent ? "current" : ""}`}
                            title={`Step ${aIdx + 1}: ${act.title}`}
                          >
                            <span className="pill-dot"></span>
                            <span className="pill-text">Step {aIdx + 1}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* CURRENT ACTIVE STEP CARD */}
                <div className="guided-interactive-card">
                  <div className="card-top-meta">
                    <div className="giant-step-number">
                      {String(guidedSession.progress?.current || 1).padStart(2, "0")}
                    </div>
                    <div className="step-header-info">
                      <div className="badges-line">
                        <span className={`safety-badge ${guidedSession.current_action?.safety_level?.toLowerCase().includes("reset") ? "caution" : "safe"}`}>
                          <ShieldCheck size={13} />
                          {guidedSession.current_action?.safety_level || "Safe"}
                        </span>
                        <span className="time-badge">
                          <Clock size={13} />
                          {guidedSession.current_action?.estimated_time || "1 min"}
                        </span>
                        <span className="type-badge">{guidedSession.current_action?.type || "Manual"}</span>
                      </div>
                      <h2 className="guided-step-title">{guidedSession.current_action?.title}</h2>
                    </div>
                  </div>

                  <p className="guided-step-desc">{guidedSession.current_action?.description}</p>

                  {/* SETTINGS PATHWAY */}
                  {guidedSession.current_action?.settings_path && (
                    <div className="guided-pathway-box">
                      <div className="pathway-info">
                        <span className="pathway-label">NAVIGATE ON YOUR DEVICE:</span>
                        <div className="pathway-string">{guidedSession.current_action.settings_path}</div>
                      </div>
                      <button
                        className="copy-pathway-btn"
                        onClick={() => copyToClipboard(guidedSession.current_action.settings_path, "guided-path")}
                      >
                        {copiedKey === "guided-path" ? <Check size={14} /> : <Copy size={14} />}
                        <span>{copiedKey === "guided-path" ? "Copied" : "Copy Path"}</span>
                      </button>
                    </div>
                  )}

                  {/* CHECKLIST INSTRUCTIONS */}
                  {guidedSession.current_action?.instructions && (
                    <div className="interactive-checklist">
                      <span className="checklist-title">Execution Checklist:</span>
                      <div className="checklist-items">
                        {guidedSession.current_action.instructions.map((inst, iIdx) => {
                          const key = `${guidedSession.progress?.current || 1}-${iIdx}`;
                          const isChecked = !!checkedItems[key];
                          return (
                            <div
                              key={iIdx}
                              className={`check-item ${isChecked ? "checked" : ""}`}
                              onClick={() => toggleInstructionCheck(guidedSession.progress?.current || 1, iIdx)}
                            >
                              <div className={`custom-checkbox ${isChecked ? "checked" : ""}`}>
                                {isChecked && <Check size={12} />}
                              </div>
                              <span className="check-text">{inst}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* PRO TIP */}
                  {guidedSession.current_action?.tip && (
                    <div className="guided-tip-box">
                      <Sparkles size={16} className="tip-icon" />
                      <div className="tip-content">
                        <strong>Technician Tip:</strong>
                        <p>{guidedSession.current_action.tip}</p>
                      </div>
                    </div>
                  )}

                  {/* CONTROLS */}
                  <div className="guided-controls-bar">
                    <div className="left-controls">
                      {(guidedSession.progress?.current || 1) > 1 && (
                        <button
                          className="guided-secondary-btn"
                          onClick={() => updateGuidedStep("prev")}
                          disabled={loading}
                        >
                          <ArrowLeft size={16} />
                          <span>Previous Step</span>
                        </button>
                      )}

                      <button
                        className="guided-ghost-btn"
                        onClick={() => updateGuidedStep("skip", "skipped")}
                        disabled={loading}
                      >
                        <span>Skip Step</span>
                      </button>
                    </div>

                    <div className="right-controls">
                      <button
                        className="guided-not-helped-btn"
                        onClick={() => updateGuidedStep("next", "not_helped")}
                        disabled={loading}
                        title="Move to next step without resolving"
                      >
                        <span>Didn't Help</span>
                      </button>

                      <button
                        className="guided-complete-btn"
                        onClick={() => updateGuidedStep("next", "helped")}
                        disabled={loading}
                      >
                        <span>I've Completed This Step</span>
                        <ArrowRight size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : unresolvedEscalation ? (
              /* SMART ESCALATION VIEW (IF ISSUE PERSISTS AFTER ALL STEPS) */
              <div className="escalation-view-card">
                <div className="escalation-badge danger">
                  <AlertTriangle size={24} />
                </div>
                <h2>Next Level Support & Hardware Diagnostics</h2>
                <p className="escalation-desc">
                  Since standard software optimizations did not resolve your issue, here are the official next steps to isolate hardware components or request service:
                </p>

                <div className="escalation-options-grid">
                  <div className="escalation-card">
                    <div className="card-step-num">01</div>
                    <div className="card-content">
                      <h4>Run Samsung Members Hardware Test</h4>
                      <p>
                        Open the <strong>Samsung Members</strong> app on your device &gt; tap <strong>Support</strong> &gt;{" "}
                        <strong>Phone Diagnostics</strong>. Test Battery, Display, Sensors, and Charging Port.
                      </p>
                    </div>
                  </div>

                  <div className="escalation-card">
                    <div className="card-step-num">02</div>
                    <div className="card-content">
                      <h4>Boot into Safe Mode</h4>
                      <p>
                        Press &amp; hold the Power button &gt; long-press the red <strong>Power off</strong> icon &gt; tap{" "}
                        <strong>Safe mode</strong>. If the issue disappears in Safe mode, a 3rd party app is responsible.
                      </p>
                    </div>
                  </div>

                  <div className="escalation-card">
                    <div className="card-step-num">03</div>
                    <div className="card-content">
                      <h4>Samsung Authorized Care</h4>
                      <p>
                        Book a walk-in appointment at a Samsung Experience Store or authorized service center for battery / screen hardware diagnostic.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="escalation-actions">
                  <button className="primary-action-btn" onClick={resetGuidedSession}>
                    <RotateCcw size={16} />
                    <span>Restart Troubleshooting Steps</span>
                  </button>
                  <button className="secondary-action-btn" onClick={resetApp}>
                    <span>Describe Another Issue</span>
                  </button>
                </div>
              </div>
            ) : (
              /* COMPLETION RESOLUTION VIEW */
              <div className="completion-resolution-card">
                <div className="celebration-icon">
                  <CheckCircle2 size={42} />
                </div>

                <div className="badge-pill success">
                  <span>TROUBLESHOOTING FINISHED</span>
                </div>

                <h2 className="completion-title">You've executed the troubleshooting path.</h2>
                <p className="completion-subtitle">
                  {guidedSession.verification?.question || "Is your Galaxy device operating smoothly now?"}
                </p>

                {/* RESOLUTION QUESTION BUTTONS */}
                <div className="resolution-options">
                  <button
                    className="resolution-btn success"
                    onClick={() => {
                      alert("Awesome! FIXORA has marked this issue as resolved. Keep your device updated!");
                      resetApp();
                    }}
                  >
                    <CheckCircle2 size={18} />
                    <span>Yes, My Device is Fixed!</span>
                  </button>

                  <button
                    className="resolution-btn warning"
                    onClick={() => setUnresolvedEscalation(true)}
                  >
                    <HelpCircle size={18} />
                    <span>No, Issue Persists (View Escalation)</span>
                  </button>
                </div>

                {/* PREVENTIVE TIPS */}
                <div className="preventive-care-box">
                  <h4>💡 Proactive Device Care Tips</h4>
                  <ul>
                    <li>Schedule an Auto-Restart once weekly in <strong>Device Care &gt; Auto optimization</strong>.</li>
                    <li>Keep storage below 85% capacity to prevent NAND flash memory write delays.</li>
                    <li>In <strong>Battery Protection</strong>, limit charging to 80% if you keep your phone plugged in overnight.</li>
                  </ul>
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-left">
          <strong>FIXORA</strong>
          <span>• Smart Guided Galaxy Diagnostics &amp; Troubleshooting Engine</span>
        </div>
        <div className="footer-right">
          <span>FastAPI 2.0 Backend</span>
          <span>• Non-destructive Repair Guides</span>
        </div>
      </footer>
    </div>
  );
}

export default App;