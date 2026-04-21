import React, { useLayoutEffect, useMemo, useRef, useState } from 'react';
import type { Answer, Question } from '../types';
import { GAME_LEVELS, selectQuestionsForLevel, type GameLevel } from '../gameConfig';
import { shuffleArray } from '../util';

type Props = {
  allQuestions: Question[];
  onExit: () => void;
  scrollContainerRef?: React.RefObject<HTMLDivElement>;
};

type GameScreen =
  | { kind: 'level_intro'; levelIndex: number }
  | { kind: 'playing'; levelIndex: number; questions: Question[] }
  | { kind: 'level_result'; levelIndex: number; answers: Answer[]; questions: Question[] }
  | { kind: 'game_complete' };

const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

export function Game({ allQuestions, onExit, scrollContainerRef }: Props) {
  const [screen, setScreen] = useState<GameScreen>({
    kind: 'level_intro',
    levelIndex: 0,
  });

  useLayoutEffect(() => {
    if (scrollContainerRef?.current) scrollContainerRef.current.scrollTop = 0;
    window.scrollTo(0, 0);
  }, [screen]);

  const startLevel = (levelIndex: number) => {
    const level = GAME_LEVELS[levelIndex];
    const questions = selectQuestionsForLevel(level, allQuestions);
    setScreen({ kind: 'playing', levelIndex, questions });
  };

  if (screen.kind === 'level_intro') {
    const level = GAME_LEVELS[screen.levelIndex];
    return (
      <LevelIntro
        level={level}
        totalLevels={GAME_LEVELS.length}
        onStart={() => startLevel(screen.levelIndex)}
        onExit={onExit}
      />
    );
  }

  if (screen.kind === 'playing') {
    return (
      <LevelPlay
        level={GAME_LEVELS[screen.levelIndex]}
        questions={screen.questions}
        scrollContainerRef={scrollContainerRef}
        onFinish={(answers) =>
          setScreen({
            kind: 'level_result',
            levelIndex: screen.levelIndex,
            answers,
            questions: screen.questions,
          })
        }
      />
    );
  }

  if (screen.kind === 'level_result') {
    const level = GAME_LEVELS[screen.levelIndex];
    const correct = screen.answers.filter((a) => a.correct).length;
    const passed = correct >= level.passThreshold;
    const isLastLevel = screen.levelIndex >= GAME_LEVELS.length - 1;

    return (
      <LevelResult
        level={level}
        answers={screen.answers}
        questions={screen.questions}
        passed={passed}
        onRetry={() => setScreen({ kind: 'level_intro', levelIndex: screen.levelIndex })}
        onNextLevel={() => {
          if (isLastLevel) {
            setScreen({ kind: 'game_complete' });
          } else {
            setScreen({ kind: 'level_intro', levelIndex: screen.levelIndex + 1 });
          }
        }}
        onExit={onExit}
        isLastLevel={isLastLevel}
      />
    );
  }

  if (screen.kind === 'game_complete') {
    return <GameComplete onExit={onExit} onPlayAgain={() => setScreen({ kind: 'level_intro', levelIndex: 0 })} />;
  }

  return null;
}

/* ------------------------------------------------------------------ */
/*  Level Intro                                                        */
/* ------------------------------------------------------------------ */

function LevelIntro({
  level,
  totalLevels,
  onStart,
  onExit,
}: {
  level: GameLevel;
  totalLevels: number;
  onStart: () => void;
  onExit: () => void;
}) {
  return (
    <div className="container container-with-bottom-bar">
      <div className="game-level-intro">
        <p className="game-level-kicker">
          Level {level.level} of {totalLevels}
        </p>
        <h1 className="game-level-name">{level.name}</h1>
        <p className="game-level-desc">{level.description}</p>
        <div className="game-level-stats">
          <div className="game-stat">
            <span className="game-stat-value">{level.questionsPerRound}</span>
            <span className="game-stat-label">Questions</span>
          </div>
          <div className="game-stat">
            <span className="game-stat-value">{level.passThreshold}</span>
            <span className="game-stat-label">To pass</span>
          </div>
        </div>
        <div className="game-level-progress">
          {Array.from({ length: totalLevels }).map((_, i) => (
            <div
              key={i}
              className={`game-level-dot ${
                i < level.level - 1
                  ? 'game-level-dot-done'
                  : i === level.level - 1
                    ? 'game-level-dot-current'
                    : ''
              }`}
            />
          ))}
        </div>
      </div>
      <div className="bottom-bar">
        <div className="bottom-bar-inner">
          <button className="ghost" onClick={onExit}>
            Quit
          </button>
          <button className="primary primary-accent" onClick={onStart}>
            Start level
          </button>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Level Play (quiz flow within a game level)                         */
/* ------------------------------------------------------------------ */

function LevelPlay({
  level,
  questions,
  scrollContainerRef,
  onFinish,
}: {
  level: GameLevel;
  questions: Question[];
  scrollContainerRef?: React.RefObject<HTMLDivElement>;
  onFinish: (answers: Answer[]) => void;
}) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
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
  React.useEffect(() => {
    if (selected === null) return;
    const timer = setTimeout(() => {
      explanationRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 350);
    return () => clearTimeout(timer);
  }, [selected]);

  if (!q) return null;

  const answered = selected !== null;
  const correctSoFar = answers.filter((a) => a.correct).length;

  const handleSelect = (i: number) => {
    if (answered) return;
    setSelected(i);
    setAnswers([
      ...answers,
      { questionId: q.id, chosenIndex: i, chosenText: shuffledChoices[i].text, correct: shuffledChoices[i].correct },
    ]);
  };

  const next = () => {
    if (scrollContainerRef?.current) scrollContainerRef.current.scrollTop = 0;
    window.scrollTo(0, 0);

    if (index + 1 >= questions.length) {
      onFinish([...answers]);
    } else {
      setIndex(index + 1);
      setSelected(null);
    }
  };

  const wasCorrect = answered && selected !== null && shuffledChoices[selected].correct;
  const progressPct = ((index + (answered ? 1 : 0)) / questions.length) * 100;

  const shouldCollapse = answered && !wasCorrect;

  return (
    <div className="container container-with-bottom-bar">
      {/* Level badge + score tracker */}
      <div className="game-play-header">
        <span className="game-play-level">Lvl {level.level} · {level.name}</span>
        <span className="game-play-score">
          {correctSoFar + (answered && wasCorrect ? 1 : 0)} / {level.passThreshold} needed
        </span>
      </div>

      <div className="quiz-progress-bar">
        <div className="quiz-progress-fill" style={{ width: `${progressPct}%` }} />
      </div>

      {q.visual && (
        <div className="quiz-hero">
          <img src={q.visual.url} alt={q.visual.alt} />
          {q.visual.credit && <div className="quiz-hero-credit">{q.visual.credit}</div>}
        </div>
      )}

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
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Level Result                                                       */
/* ------------------------------------------------------------------ */

function LevelResult({
  level,
  answers,
  questions,
  passed,
  onRetry,
  onNextLevel,
  onExit,
  isLastLevel,
}: {
  level: GameLevel;
  answers: Answer[];
  questions: Question[];
  passed: boolean;
  onRetry: () => void;
  onNextLevel: () => void;
  onExit: () => void;
  isLastLevel: boolean;
}) {
  const correct = answers.filter((a) => a.correct).length;
  const total = answers.length;
  const pct = total === 0 ? 0 : Math.round((correct / total) * 100);

  return (
    <div className="container container-with-bottom-bar">
      <div className="game-result-badge-wrapper">
        <div className={`game-result-badge ${passed ? 'game-result-badge-pass' : 'game-result-badge-fail'}`}>
          {passed ? '✓' : '✗'}
        </div>
      </div>

      <p className="game-result-kicker">
        Level {level.level} · {level.name}
      </p>
      <h1 className="game-result-heading">
        {passed ? 'Level cleared!' : 'Not quite.'}
      </h1>
      <p className="game-result-score">
        <span className="game-result-score-figure">
          {correct} of {total}
        </span>{' '}
        correct ({pct}%) — needed {level.passThreshold}
      </p>

      {!passed && (
        <p className="game-result-encourage">
          You'll get different questions next time. Give it another shot.
        </p>
      )}

      {/* Question review */}
      <p className="section-label" style={{ marginTop: 8 }}>
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
          {passed ? (
            <>
              <button className="ghost" onClick={onExit}>
                Quit
              </button>
              <button className="primary primary-accent" onClick={onNextLevel}>
                {isLastLevel ? 'Finish' : 'Next level →'}
              </button>
            </>
          ) : (
            <>
              <button className="ghost" onClick={onExit}>
                Quit
              </button>
              <button className="primary primary-accent" onClick={onRetry}>
                Try again
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Game Complete                                                       */
/* ------------------------------------------------------------------ */

function GameComplete({
  onExit,
  onPlayAgain,
}: {
  onExit: () => void;
  onPlayAgain: () => void;
}) {
  return (
    <div className="container container-with-bottom-bar">
      <div className="game-complete">
        <div className="game-complete-icon">🏆</div>
        <h1 className="game-complete-heading">Grandmaster.</h1>
        <p className="game-complete-text">
          You cleared every level. Not many people can say that.
        </p>
      </div>

      <div className="bottom-bar">
        <div className="bottom-bar-inner">
          <button className="ghost" onClick={onPlayAgain}>
            Play again
          </button>
          <button className="primary" onClick={onExit}>
            Back to home
          </button>
        </div>
      </div>
    </div>
  );
}
