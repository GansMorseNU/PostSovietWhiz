import type { Answer, Question } from '../types';
import { pretty } from '../App';

type Props = {
  target: string;
  questions: Question[];
  answers: Answer[];
  onRestart: () => void;
};

export function Results({ target, questions, answers, onRestart }: Props) {
  const correct = answers.filter((a) => a.correct).length;
  const total = answers.length;
  const pct = total === 0 ? 0 : Math.round((correct / total) * 100);

  return (
    <div className="container container-with-bottom-bar">
      <p className="results-kicker">{pretty(target)} · Results</p>
      <h1 className="results-heading">
        {correct} of {total}
      </h1>
      <p className="results-score">
        <span className="results-score-figure">{pct}%</span> correct
      </p>

      <p className="section-label" style={{ marginTop: 0 }}>
        Review
      </p>
      <ol className="review">
        {questions.map((q) => {
          const a = answers.find((x) => x.questionId === q.id);
          const correctChoice = q.choices.find((c) => c.correct);
          const isCorrect = !!a?.correct;
          return (
            <li key={q.id}>
              <p
                className={`review-mark ${
                  isCorrect ? 'review-mark-correct' : 'review-mark-wrong'
                }`}
              >
                {isCorrect ? 'Correct' : 'Incorrect'}
              </p>
              <p className="review-prompt">{q.prompt}</p>
              <p className="review-answer">
                {a ? (
                  <>
                    Your answer: <em>{a.chosenText}</em>
                    {!isCorrect && correctChoice && (
                      <>
                        {' '}· Correct: <strong>{correctChoice.text}</strong>
                      </>
                    )}
                  </>
                ) : (
                  <em>Not answered</em>
                )}
              </p>
            </li>
          );
        })}
      </ol>

      <div className="bottom-bar">
        <div className="bottom-bar-inner">
          <button className="primary" onClick={onRestart}>
            Back to categories
          </button>
        </div>
      </div>
    </div>
  );
}
