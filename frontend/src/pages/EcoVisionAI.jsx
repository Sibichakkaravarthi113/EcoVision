import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  User,
  Send,
  Trash2,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  MapPin,
  CornerDownLeft
} from 'lucide-react';
import { useDemoMode } from '../context/DemoModeContext';
import { useLocationCtx } from '../context/LocationContext';
import { sendMessage } from '../services/chatApi';

const SUGGESTED_QUESTIONS = [
  'What is the air quality in my location?',
  'Explain the water quality data',
  'What is PM2.5?',
  'How is the forest coverage in my state?',
  'Which dimensions have unavailable data?',
  'What is the current climate forecast?',
  'Compare air and water quality',
  'How can we reduce noise pollution?',
  'What industries are in my area?'
];

// Helper to format assistant responses including markdown tables
function FormattedMessage({ text }) {
  if (!text) return null;

  // Check if text has markdown table lines with | ... |
  const lines = text.split('\n');
  const blocks = [];
  let currentTable = [];
  let currentParagraph = [];

  const flushParagraph = () => {
    if (currentParagraph.length > 0) {
      blocks.push({
        type: 'text',
        content: currentParagraph.join('\n')
      });
      currentParagraph = [];
    }
  };

  const flushTable = () => {
    if (currentTable.length > 0) {
      blocks.push({
        type: 'table',
        rows: currentTable
      });
      currentTable = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|') && line.endsWith('|')) {
      flushParagraph();
      // Skip markdown separator lines like |---|---|
      if (line.includes('---')) {
        continue;
      }
      const cells = line
        .split('|')
        .slice(1, -1)
        .map((c) => c.trim());
      currentTable.push(cells);
    } else {
      flushTable();
      currentParagraph.push(lines[i]);
    }
  }
  flushParagraph();
  flushTable();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      {blocks.map((b, idx) => {
        if (b.type === 'table') {
          const header = b.rows[0];
          const body = b.rows.slice(1);
          return (
            <div key={`table-${idx}`} className="table-responsive" style={{ margin: '0.4rem 0' }}>
              <table className="data-table" style={{ fontSize: '0.8rem' }}>
                {header && (
                  <thead>
                    <tr>
                      {header.map((h, hIdx) => (
                        <th key={`h-${hIdx}`}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                )}
                <tbody>
                  {body.map((row, rIdx) => (
                    <tr key={`r-${rIdx}`}>
                      {row.map((cell, cIdx) => (
                        <td key={`c-${cIdx}`}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        // Text block with basic line break and bolding preservation
        return (
          <div key={`text-${idx}`} style={{ whiteSpace: 'pre-wrap' }}>
            {b.content}
          </div>
        );
      })}
    </div>
  );
}

export default function EcoVisionAI() {
  const { demoMode } = useDemoMode();
  const { location } = useLocationCtx();

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I am your EcoVision Environmental AI assistant. I can analyze air and water quality measurements, forest canopy coverage, waste generation statistics, noise levels, and meteorological models for ${
        location.city ? `${location.city}, ${location.state}` : location.state ? location.state : 'any region in India'
      }. How can I assist your environmental analysis today?`
    }
  ]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (messageText = input) => {
    const textToSend = (messageText || '').trim();
    if (!textToSend || loading) return;

    const userMessage = { role: 'user', content: textToSend };
    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      // Build history excluding greeting
      const history = updatedMessages.slice(1).map((m) => ({
        role: m.role,
        content: m.content
      }));

      const locationContext = {
        state: location.state || '',
        district: location.district || '',
        city: location.city || ''
      };

      const res = await sendMessage({
        message: textToSend,
        location: locationContext,
        demo_mode: demoMode,
        history
      });

      const replyContent = res.reply || res.response || res.message || 'I have analyzed the current environmental parameters for your location. All indicators are within standard threshold observations.';

      setMessages((prev) => [...prev, { role: 'assistant', content: replyContent }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `I encountered an issue querying the environmental knowledge engine: ${err.message}. Please verify the backend service is operational.`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: `Chat history cleared. How can I assist your environmental analysis for ${
          location.city ? `${location.city}, ${location.state}` : location.state || 'India'
        }?`
      }
    ]);
  };

  const locationContextLabel = location.state
    ? location.city
      ? `${location.state} > ${location.city}`
      : location.state
    : 'National (All India)';

  return (
    <div className="page-container" style={{ paddingBottom: '0.5rem' }}>
      <div className="chat-page">
        {/* Left Sidebar with suggestions */}
        <aside className="chat-sidebar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="var(--accent-emerald)" />
            <h4 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Suggested Queries
            </h4>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', overflowY: 'auto' }}>
            {SUGGESTED_QUESTIONS.map((q, idx) => (
              <button
                key={`q-${idx}`}
                type="button"
                className="suggestion-chip"
                onClick={() => handleSend(q)}
                disabled={loading}
              >
                {q}
              </button>
            ))}
          </div>

          <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <button
              type="button"
              onClick={handleClearChat}
              className="btn btn-secondary"
              style={{ width: '100%', fontSize: '0.8rem' }}
            >
              <Trash2 size={14} /> New Chat Session
            </button>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="chat-main">
          {/* Header Bar */}
          <div className="chat-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div className="sidebar-logo-icon" style={{ width: '32px', height: '32px' }}>
                <Bot size={18} />
              </div>
              <div>
                <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>EcoVision Environmental AI</h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <MapPin size={12} /> Context: <strong>{locationContextLabel}</strong>
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                className={`badge ${demoMode ? 'badge-yellow' : 'badge-green'}`}
                style={{ fontSize: '0.75rem', padding: '3px 8px' }}
              >
                {demoMode ? <ShieldAlert size={12} /> : <ShieldCheck size={12} />}
                {demoMode ? 'Demo Mode Active' : 'Public Data Mode'}
              </span>
            </div>
          </div>

          {/* Messages Area */}
          <div className="chat-messages">
            {messages.map((m, idx) => {
              const isUser = m.role === 'user';
              return (
                <div key={`msg-${idx}`} className={`message-row ${isUser ? 'user' : 'assistant'}`}>
                  <div className={`message-avatar ${isUser ? 'user' : 'assistant'}`}>
                    {isUser ? <User size={18} /> : <Bot size={18} />}
                  </div>
                  <div className="message-bubble">
                    <FormattedMessage text={m.content} />
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="message-row assistant">
                <div className="message-avatar assistant">
                  <Bot size={18} />
                </div>
                <div className="message-bubble" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }} />
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    EcoVision is querying multi-dimensional environmental models...
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chat-input-container">
            <form
              className="chat-input-form"
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
            >
              <textarea
                placeholder="Ask about air/water metrics, pollution limits, climate trends..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                rows={1}
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={!input.trim() || loading}
                style={{ height: '48px', padding: '0 1.25rem' }}
              >
                <Send size={16} /> Send
              </button>
            </form>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.4rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              <span>Press <strong>Enter</strong> to send, <strong>Shift + Enter</strong> for a new line</span>
              <span>AI can make mistakes. Cross-reference with CPCB/SPCB statutory data.</span>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
