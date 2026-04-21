import { useLayoutEffect, useRef, useState } from 'react';
import questionsData from '../../content/questions.sample.json';
import type { Answer, CountryFilter, DifficultyFilter, EraFilter, Question, QuestionBank } from './types';
import { Start } from './components/Start';
import { Home } from './components/Home';
import { Quiz } from './components/Quiz';
import { Results } from './components/Results';
import { Game } from './components/Game';

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

type Filters = {
  difficulty: DifficultyFilter;
  era: EraFilter;
  country: CountryFilter;
};

type Screen =
  | { kind: 'start' }
  | { kind: 'home' }
  | { kind: 'quiz'; target: QuizTarget; filters: Filters }
  | { kind: 'results'; answers: Answer[]; target: QuizTarget; filters: Filters }
  | { kind: 'game' };

const bank = questionsData as QuestionBank;

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
  if (s.kind === 'game') return 'game';
  return 'quiz';
}

export function App() {
  const [screen, setScreen] = useState<Screen>({ kind: 'start' });
  const [difficulty, setDifficulty] = useState<DifficultyFilter>('mix');
  const [era, setEra] = useState<EraFilter>('all');
  const [country, setCountry] = useState<CountryFilter>('all');
  const appRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    if (appRef.current) appRef.current.scrollTop = 0;
    window.scrollTo(0, 0);
  }, [screen.kind]);

  const mode = screenMode(screen);
  const currentFilters: Filters = { difficulty, era, country };

  const goBack = () => {
    if (screen.kind === 'quiz' || screen.kind === 'results') {
      setScreen({ kind: 'home' });
    } else if (screen.kind === 'home') {
      setScreen({ kind: 'start' });
    } else {
      setScreen({ kind: 'start' });
    }
  };

  const topbarLabel = (): string => {
    if (mode === 'game') return 'Game Mode';
    if (screen.kind === 'home') return 'Quiz Mode';
    if (screen.kind === 'quiz') return pretty(screen.target);
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
          onGameMode={() => setScreen({ kind: 'game' })}
        />
      )}

      {screen.kind === 'home' && (
        <Home
          difficulty={difficulty}
          onChangeDifficulty={setDifficulty}
          era={era}
          onChangeEra={setEra}
          country={country}
          onChangeCountry={setCountry}
          countFor={(target) => filterQuestions(target, currentFilters).length}
          onStartQuiz={(target) =>
            setScreen({ kind: 'quiz', target, filters: currentFilters })
          }
        />
      )}

      {screen.kind === 'quiz' && (
        <Quiz
          questions={filterQuestions(screen.target, screen.filters)}
          scrollContainerRef={appRef}
          onFinish={(answers) =>
            setScreen({
              kind: 'results',
              answers,
              target: screen.target,
              filters: screen.filters,
            })
          }
        />
      )}

      {screen.kind === 'results' && (
        <Results
          target={screen.target}
          questions={filterQuestions(screen.target, screen.filters)}
          answers={screen.answers}
          onRestart={() => setScreen({ kind: 'home' })}
        />
      )}

      {screen.kind === 'game' && (
        <Game
          allQuestions={bank.questions}
          onExit={() => setScreen({ kind: 'start' })}
          scrollContainerRef={appRef}
        />
      )}
    </div>
  );
}
