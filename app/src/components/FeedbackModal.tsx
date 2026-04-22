import { useEffect, useMemo, useState } from 'react';
import type { Question } from '../types';
import {
  DIFFICULTY_LEVELS,
  isFeedbackEndpointConfigured,
  submitFeedback,
  type DifficultyLevel,
  type FeedbackContext,
  type FeedbackKind,
} from '../feedback';

type Props = {
  isOpen: boolean;
  onClose: () => void;
  question: Question;
  context: FeedbackContext;
};

const FEEDBACK_OPTIONS: { value: FeedbackKind; label: string }[] = [
  { value: 'fact_error', label: 'Fact is wrong' },
  { value: 'reword', label: 'Should be reworded' },
  { value: 'difficulty', label: 'Level of difficulty is miscategorized' },
  { value: 'distractors', label: 'Answer choices are weak' },
  { value: 'game_level', label: 'Wrong for this game level' },
  { value: 'bug', label: 'App bug / UX issue' },
  { value: 'other', label: 'Other' },
];

function surfaceLabel(context: FeedbackContext): string {
  if (context.surface === 'game' && context.gameLevel) {
    return `Game mode · Level ${context.gameLevel.level} (${context.gameLevel.name})`;
  }
  if (context.surface === 'game_results') return 'Game mode review';
  if (context.surface === 'quiz_results') return 'Quiz results review';
  return 'Quiz mode';
}

export function FeedbackModal({ isOpen, onClose, question, context }: Props) {
  const endpointConfigured = useMemo(() => isFeedbackEndpointConfigured(), []);
  const [kind, setKind] = useState<FeedbackKind>('fact_error');
  const [details, setDetails] = useState('');
  const [suggestedRewrite, setSuggestedRewrite] = useState('');
  const [suggestedDifficulty, setSuggestedDifficulty] = useState<DifficultyLevel | ''>('');
  const [reporter, setReporter] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setKind('fact_error');
    setDetails('');
    setSuggestedRewrite('');
    setSuggestedDifficulty('');
    setReporter('');
    setStatusMessage('');
  }, [isOpen, question.id]);

  useEffect(() => {
    if (!isOpen) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previous;
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const contextParts = [
    surfaceLabel(context),
    context.questionPosition
      ? `Question ${context.questionPosition.current} of ${context.questionPosition.total}`
      : null,
    question.difficulty,
    question.era,
    question.country,
  ].filter(Boolean);

  const isDifficultyKind = kind === 'difficulty';
  const currentDifficultyLabel =
    DIFFICULTY_LEVELS.find((l) => l.value === question.difficulty)?.label ??
    question.difficulty;

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);

    const result = await submitFeedback({
      question,
      context,
      kind,
      details: details.trim(),
      suggestedRewrite: suggestedRewrite.trim(),
      suggestedDifficulty: isDifficultyKind && suggestedDifficulty ? suggestedDifficulty : undefined,
      reporter: reporter.trim(),
    });

    setStatusMessage(result.message);
    setSubmitting(false);
  };

  return (
    <div className="feedback-overlay" onClick={onClose}>
      <div
        className="feedback-modal"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="feedback-title"
      >
        <div className="feedback-header">
          <div>
            <p className="feedback-kicker">Question feedback</p>
            <h2 id="feedback-title" className="feedback-title">
              {question.id}
            </h2>
          </div>
          <button className="feedback-close" onClick={onClose} aria-label="Close feedback">
            ×
          </button>
        </div>

        <p className="feedback-context">
          {contextParts.join(' · ')}
        </p>
        <p className="feedback-prompt">{question.prompt}</p>

        <form className="feedback-form" onSubmit={handleSubmit}>
          <label className="feedback-field">
            <span className="feedback-label">Type</span>
            <select
              className="feedback-select"
              value={kind}
              onChange={(event) => setKind(event.target.value as FeedbackKind)}
            >
              {FEEDBACK_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          {isDifficultyKind && (
            <div className="feedback-field feedback-difficulty-block">
              <span className="feedback-label">Correct difficulty</span>
              <p className="feedback-difficulty-current">
                Current: <strong>{currentDifficultyLabel}</strong>
              </p>
              <div className="feedback-difficulty-options" role="radiogroup" aria-label="Correct difficulty">
                {DIFFICULTY_LEVELS.map((level) => {
                  const isCurrent = level.value === question.difficulty;
                  return (
                    <label
                      key={level.value}
                      className={`feedback-difficulty-option${
                        isCurrent ? ' is-current' : ''
                      }${suggestedDifficulty === level.value ? ' is-selected' : ''}`}
                    >
                      <input
                        type="radio"
                        name="suggested-difficulty"
                        value={level.value}
                        checked={suggestedDifficulty === level.value}
                        disabled={isCurrent}
                        onChange={() => setSuggestedDifficulty(level.value)}
                      />
                      <span>{level.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          <label className="feedback-field">
            <span className="feedback-label">
              {isDifficultyKind ? 'Notes (optional)' : 'What should change?'}
            </span>
            <textarea
              className="feedback-textarea"
              value={details}
              onChange={(event) => setDetails(event.target.value)}
              rows={isDifficultyKind ? 3 : 5}
              required={!isDifficultyKind}
              placeholder={
                isDifficultyKind
                  ? 'Optional: explain why you’d re-level this.'
                  : 'Example: This fact is wrong; the correct year is 1994.'
              }
            />
          </label>

          <label className="feedback-field">
            <span className="feedback-label">Suggested rewrite (optional)</span>
            <textarea
              className="feedback-textarea"
              value={suggestedRewrite}
              onChange={(event) => setSuggestedRewrite(event.target.value)}
              rows={4}
              placeholder="Optional revised prompt, answer choice, or explanation."
            />
          </label>

          <label className="feedback-field">
            <span className="feedback-label">Name / signature (optional)</span>
            <input
              className="feedback-input"
              value={reporter}
              onChange={(event) => setReporter(event.target.value)}
              placeholder="Optional name or signature."
            />
          </label>

          {!endpointConfigured && (
            <p className="feedback-help">
              Google Sheets sync is not configured yet, so reports will be saved locally on this
              device for now.
            </p>
          )}
          {statusMessage && <p className="feedback-status">{statusMessage}</p>}

          <div className="feedback-actions">
            <button type="button" className="ghost" onClick={onClose}>
              Close
            </button>
            <button
              type="submit"
              className="primary primary-accent"
              disabled={submitting || (isDifficultyKind && !suggestedDifficulty)}
            >
              {submitting ? 'Sending…' : endpointConfigured ? 'Send feedback' : 'Save feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
