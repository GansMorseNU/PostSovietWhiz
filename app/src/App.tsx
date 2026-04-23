import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import questionsData from '../../content/questions.sample.json';
import type { Answer, CountryFilter, DifficultyFilter, EraFilter, Question, QuestionBank } from './types';
import { Start } from './components/Start';
import { Home } from './components/Home';
import { Quiz } from './components/Quiz';
import { Results } from './components/Results';
import { Game } from './components/Game';
import { GameSetup } from './components/GameSetup';
import { retryPendingFeedback } from './feedback';
import { logSessionStart, retryPendingAnalytics } from './analytics';
import { shuffleArray } from './util';

export const APP_NAME = 'PostSovietWhiz';

/* ------------------------------------------------------------------ */
/*  Categories                                                         */
/* ------------------------------------------------------------------ */

export type CategoryDef = {
  key: string;
  name: string;
  description: string;
};

export const CATEGORIES: CategoryDef[] = [
  {
    key: 'political_transitions',
    name: 'Political Transitions',
    description: 'Democratization, nationalism, regime change, and sovereignty politics.',
  },
  {
    key: 'economic_transitions',
    name: 'Economic Transitions',
    description: 'Market reforms, privatization, and post-Soviet political economy.',
  },
  {
    key: 'foreign_policy',
    name: 'Foreign Policy',
    description: 'Russia-West relations, post-Soviet order, and geopolitics.',
  },
];

/* ------------------------------------------------------------------ */
/*  Screens                                                            */
/* ------------------------------------------------------------------ */

/** Quiz target: 'all' or a category key */
export type QuizTarget = string;

export type Filters = {
  difficulty: DifficultyFilter;
  era: EraFilter;
  country: CountryFilter;
};

type QuizSession = {
  target: QuizTarget;
  filters: Filters;
  currentQuestions: Question[];
  remainingQuestions: Question[];
  batchNumber: number;
  mode: 'standard' | 'redo';
};

type Screen =
  | { kind: 'start' }
  | { kind: 'home' }
  | { kind: 'quiz'; session: QuizSession }
  | { kind: 'results'; answers: Answer[]; session: QuizSession }
  | { kind: 'game_setup' }
  | { kind: 'game'; filters: Filters };

const bank = questionsData as QuestionBank;
const QUIZ_BATCH_SIZE = 10;
const DEFAULT_FILTERS: Filters = {
  difficulty: 'mix',
  era: 'all',
  country: 'all',
};

/* ------------------------------------------------------------------ */
/*  Filtering                                                          */
/* ------------------------------------------------------------------ */

export const filterQuestions = (
  target: QuizTarget,
  filters: Filters,
): Question[] =>
  bank.questions.filter((q) => {
    // Category filter
    if (target !== 'all' && q.category !== target) return false;
    // Difficulty
    if (filters.difficulty !== 'mix') {
      const effective = q.difficulty === 'expert' ? 'hard' : q.difficulty;
      if (effective !== filters.difficulty) return false;
    }
    // Era
    if (filters.era !== 'all') {
      const visibleEras = q.era_filter_visibility ?? [q.era];
      if (!visibleEras.includes(filters.era)) return false;
    }
    // Country: selecting 'russia' matches russia + both; 'ukraine' matches ukraine + both
    if (filters.country !== 'all') {
      if (filters.country === 'both') {
        if (q.country !== 'both') return false;
      } else {
        if (q.country !== filters.country && q.country !== 'both') return false;
      }
    }
    return true;
  });

function createQuizSession(
  target: QuizTarget,
  filters: Filters,
  questionPool: Question[],
  batchNumber = 1,
): QuizSession {
  const shuffled = shuffleArray(questionPool);
  return {
    target,
    filters: { ...filters },
    currentQuestions: shuffled.slice(0, QUIZ_BATCH_SIZE),
    remainingQuestions: shuffled.slice(QUIZ_BATCH_SIZE),
    batchNumber,
    mode: 'standard',
  };
}

function getMissedQuestions(questions: Question[], answers: Answer[]): Question[] {
  const missedIds = new Set(
    answers.filter((answer) => !answer.correct).map((answer) => answer.questionId),
  );
  return questions.filter((question) => missedIds.has(question.id));
}

/* ------------------------------------------------------------------ */
/*  Pretty names                                                       */
/* ------------------------------------------------------------------ */

const prettyNames: Record<string, string> = {
  political_transitions: 'Political Transitions',
  economic_transitions: 'Economic Transitions',
  foreign_policy: 'Foreign Policy',
  all: 'All Topics',
};

export const pretty = (target: string): string =>
  prettyNames[target] ?? target;

export const prettyDifficulty: Record<DifficultyFilter, string> = {
  mix: 'Mix',
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
  very_hard: 'Very hard',
  expert: 'Expert',
};

export const prettyEra: Record<EraFilter, string> = {
  all: 'All',
  soviet: 'Soviet',
  '1990s': '1990s',
  '2000s': '2000s',
  '2010s_plus': '2010s+',
};

export const prettyCountry: Record<CountryFilter, string> = {
  all: 'All',
  russia: 'Russia',
  ukraine: 'Ukraine',
  both: 'Comparative',
};

/* ------------------------------------------------------------------ */
/*  App                                                                */
/* ------------------------------------------------------------------ */

function screenMode(s: Screen): 'start' | 'quiz' | 'game' {
  if (s.kind === 'start') return 'start';
  if (s.kind === 'game' || s.kind === 'game_setup') return 'game';
  return 'quiz';
}

export function App() {
  const [screen, setScreen] = useState<Screen>({ kind: 'start' });
  const [quizFilters, setQuizFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [gameFilters, setGameFilters] = useState<Filters>(DEFAULT_FILTERS);
  const appRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    if (appRef.current) appRef.current.scrollTop = 0;
    window.scrollTo(0, 0);
  }, [screen.kind]);

  useEffect(() => {
    retryPendingFeedback();
    retryPendingAnalytics();
    logSessionStart();
    const handleOnline = () => {
      retryPendingFeedback();
      retryPendingAnalytics();
    };
    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, []);

  const mode = screenMode(screen);
  const startQuiz = (target: QuizTarget, filters: Filters) => {
    setScreen({
      kind: 'quiz',
      session: createQuizSession(target, filters, filterQuestions(target, filters)),
    });
  };

  const goBack = () => {
    if (screen.kind === 'quiz' || screen.kind === 'results') {
      setScreen({ kind: 'home' });
    } else if (screen.kind === 'home') {
      setScreen({ kind: 'start' });
    } else if (screen.kind === 'game') {
      setScreen({ kind: 'game_setup' });
    } else if (screen.kind === 'game_setup') {
      setScreen({ kind: 'start' });
    } else {
      setScreen({ kind: 'start' });
    }
  };

  const topbarLabel = (): string => {
    if (mode === 'game') return 'Game Mode';
    if (screen.kind === 'home') return 'Quiz Mode';
    if (screen.kind === 'quiz') return pretty(screen.session.target);
    if (screen.kind === 'results') return 'Results';
    return 'Quiz Mode';
  };

  return (
    <div className="app" ref={appRef}>
      <div className="topbar">
        <div className="topbar-inner">
          {screen.kind === 'start' ? (
            <>
              <div className="brand">
                <span className="brand-mark">■</span>
                {APP_NAME}
              </div>
              <div className="topbar-meta">Beta</div>
            </>
          ) : (
            <>
              <button
                className="topbar-back"
                onClick={goBack}
                aria-label="Back"
              >
                ‹ Back
              </button>
              <div className="topbar-meta">{topbarLabel()}</div>
              <span style={{ width: 48 }} />
            </>
          )}
        </div>
      </div>

      {screen.kind === 'start' && (
        <Start
          onQuizMode={() => setScreen({ kind: 'home' })}
          onGameMode={() => setScreen({ kind: 'game_setup' })}
        />
      )}

      {screen.kind === 'home' && (
        <Home
          difficulty={quizFilters.difficulty}
          onChangeDifficulty={(difficulty) =>
            setQuizFilters((prev) => ({ ...prev, difficulty }))
          }
          era={quizFilters.era}
          onChangeEra={(era) => setQuizFilters((prev) => ({ ...prev, era }))}
          country={quizFilters.country}
          onChangeCountry={(country) => setQuizFilters((prev) => ({ ...prev, country }))}
          countFor={(target) => filterQuestions(target, quizFilters).length}
          onStartQuiz={(target) => startQuiz(target, quizFilters)}
        />
      )}

      {screen.kind === 'game_setup' && (
        <GameSetup
          era={gameFilters.era}
          onChangeEra={(era) => setGameFilters((prev) => ({ ...prev, era }))}
          country={gameFilters.country}
          onChangeCountry={(country) => setGameFilters((prev) => ({ ...prev, country }))}
          matchingCount={filterQuestions('all', gameFilters).length}
          onStartGame={() =>
            setScreen({
              kind: 'game',
              filters: { ...gameFilters },
            })
          }
        />
      )}

      {screen.kind === 'quiz' && (
        <Quiz
          questions={screen.session.currentQuestions}
          scrollContainerRef={appRef}
          onFinish={(answers) =>
            setScreen({
              kind: 'results',
              answers,
              session: screen.session,
            })
          }
        />
      )}

      {screen.kind === 'results' && (
        <Results
          target={screen.session.target}
          mode={screen.session.mode}
          batchNumber={screen.session.batchNumber}
          questions={screen.session.currentQuestions}
          answers={screen.answers}
          remainingCount={screen.session.remainingQuestions.length}
          onContinue={
            screen.session.remainingQuestions.length > 0
              ? () =>
                  setScreen({
                    kind: 'quiz',
                    session: createQuizSession(
                      screen.session.target,
                      screen.session.filters,
                      screen.session.remainingQuestions,
                      screen.session.batchNumber + 1,
                    ),
                  })
              : undefined
          }
          onRedoMissed={
            getMissedQuestions(screen.session.currentQuestions, screen.answers).length > 0
              ? () =>
                  setScreen({
                    kind: 'quiz',
                    session: {
                      ...screen.session,
                      currentQuestions: getMissedQuestions(
                        screen.session.currentQuestions,
                        screen.answers,
                      ),
                      mode: 'redo',
                    },
                  })
              : undefined
          }
          onRestart={() => setScreen({ kind: 'home' })}
        />
      )}

      {screen.kind === 'game' && (
        <Game
          allQuestions={filterQuestions('all', screen.filters)}
          onExit={() => setScreen({ kind: 'game_setup' })}
          scrollContainerRef={appRef}
        />
      )}
    </div>
  );
}
