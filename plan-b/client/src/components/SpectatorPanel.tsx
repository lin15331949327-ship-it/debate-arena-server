/**
 * components/SpectatorPanel.tsx — 旁观者提问面板
 */

import { useState } from 'react';
import { useDebateStore } from '../store/debateStore';
import { sendSpectatorQuestion } from '../api';

export default function SpectatorPanel() {
  const [question, setQuestion] = useState('');
  const [name, setName] = useState('');
  const [sending, setSending] = useState(false);
  const debateId = useDebateStore((s) => s.debateId);
  const questions = useDebateStore((s) => s.spectatorQuestions);
  const status = useDebateStore((s) => s.status);

  const handleSubmit = async () => {
    if (!question.trim() || !debateId || sending) return;
    setSending(true);
    try {
      await sendSpectatorQuestion(debateId, question.trim(), name.trim() || undefined);
      setQuestion('');
    } catch (err: any) {
      alert(`提问失败: ${err.message}`);
    }
    setSending(false);
  };

  return (
    <div className="spectator-panel">
      <h3 className="spectator-panel__title">👁️ 旁观者提问</h3>

      <div className="spectator-panel__form">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="你的名字 (可选)"
          className="spectator-panel__name"
        />
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSubmit())}
          placeholder="向辩论者提问..."
          rows={3}
          className="spectator-panel__input"
          disabled={status !== 'running'}
        />
        <button
          onClick={handleSubmit}
          disabled={!question.trim() || sending || status !== 'running'}
          className="spectator-panel__btn"
        >
          {sending ? '发送中...' : '💬 提问'}
        </button>
      </div>

      {questions.length > 0 && (
        <div className="spectator-panel__list">
          {questions.map((q, i) => (
            <div key={i} className="spectator-panel__item">
              <span className="spectator-panel__from">{q.from}</span>
              <span className="spectator-panel__q">{q.question}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
