import { useEffect, useLayoutEffect, useMemo, useRef, useState, type RefObject } from 'react';
import type { Answer, Question } from '../types';
import { FeedbackModal } from './FeedbackModal';
import { shuffleArray } from '../util';

type Props = {
  questions: Question[];
  onFinish: (answers: Answer[]) => void;
  scrollContainerRef?: RefObject<HTMLDivElement>;
};

const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

export function Quiz({ questions, onFinish, scrollContainerRef }: Props) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const explanationRef = useRef<HTMLDivElement>(null);

  const q = questions[index];
  const shuffledChoices = useMemo(
    () => (q ? shuffleArray(q.choices) : []),
    [q],
  );

  useLayoutEffect(() => {
    if (scrollContainerRef?.current) scrollContainerRef.current.scrollTop = 0;
    window.scrollTo(0, 0);
  }, [index, scrollContainerRef]);

  // Auto-scroll to explanation after answering
  useEffect(() => {
    if (selected === null) return;
    const timer = setTimeout(() => {
      explanationRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 350);
    return () => clearTimeout(timer);
  }, [selected]);

  if (!q) return null;

  const answered = selected !== null;

  const handleSelect = (i: number) => {
    if (answered) return;
    setSelected(i);
    setAnswers([
      ...answers,
      {
        questionId: q.id,
        chosenIndex: i,
        chosenText: shuffledChoices[i].text,
        correct: shuffledChoices[i].correct,
      },
    ]);
  };

  const next = () => {
    // Force scroll to top before state update to prevent stale smooth-scroll interference
    if (scrollContainerRef?.current) scrollContainerRef.current.scrollTop = 0;
    window.scrollTo(0, 0);

    if (index + 1 >= questions.length) {
      onFinish(answers);
    } else {
      setIndex(index + 1);
      setSelected(null);
    }
  };

  const wasCorrect = answered && selected !== null && shuffledChoices[selected].correct;
  const progressPct = ((index + (answered ? 1 : 0)) / questions.length) * 100;

  // When wrong, non-selected wrong answers collapse out
  const shouldCollapse = answered && !wasCorrect;

  return (
    <div className="container container-with-bottom-bar">
      <div className="quiz-progress-bar">
        <div className="quiz-progress-fill" style={{ width: `${progressPct}%` }} />
      </div>

      {q.visual && (
        <div className="quiz-hero">
          <img src={q.visual.url} alt={q.visual.alt} />
          {q.visual.credit && <div className="quiz-hero-credit">{q.visual.credit}</div>}
        </div>
      )}

      <div className="question-meta-row">
        <p className="question-meta">
          Question {index + 1} of {questions.length} · {q.id}
        </p>
        <button className="question-feedback-trigger" onClick={() => setFeedbackOpen(true)}>
          Report
        </button>
      </div>

      <h2 className="prompt">{q.prompt}</h2>

      <ul className="choices">
        {shuffledChoices.map((c, i) => {
          const isSelected = selected === i;
          const isOtherWrong = shouldCollapse && !isSelected && !c.correct;

          let className = 'choice';
          if (answered) {
            className += ' choice-revealed';
            if (c.correct) className += ' choice-correct';
            else if (isSelected) className += ' choice-wrong';
          }
          return (
            <li key={i} className={isOtherWrong ? 'choice-li-collapsed' : ''}>
              <button
                className={className}
                disabled={answered}
                onClick={() => handleSelect(i)}
              >
                <span className="choice-letter">{LETTERS[i]}</span>
                <span className="choice-body">
                  <span className="choice-text">{c.text}</span>
                  {answered && c.note && isSelected && !c.correct && <p className="choice-note">{c.note}</p>}
                </span>
              </button>
            </li>
          );
        })}
      </ul>

      {answered && (
        <div className="explanation" ref={explanationRef}>
          <p
            className={`explanation-label ${
              wasCorrect ? 'explanation-label-correct' : 'explanation-label-wrong'
            }`}
          >
            {wasCorrect ? 'Correct' : 'Incorrect'}
          </p>
          <p>{q.explanation}</p>
        </div>
      )}

      {answered && (
        <div className="bottom-bar">
          <div className="bottom-bar-inner">
            <button className="primary primary-accent" onClick={next}>
              {index + 1 >= questions.length ? 'See results' : 'Next question'}
            </button>
          </div>
        </div>
      )}

      <FeedbackModal
        isOpen={feedbackOpen}
        onClose={() => setFeedbackOpen(false)}
        question={q}
        context={{
          surface: 'quiz',
          questionPosition: { current: index + 1, total: questions.length },
          selectedChoiceText:
            answered && selected !== null ? shuffledChoices[selected].text : undefined,
          wasCorrect: answered ? wasCorrect : undefined,
        }}
      />
    </div>
  );
}
