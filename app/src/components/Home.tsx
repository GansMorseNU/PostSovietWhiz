import { CATEGORIES, prettyDifficulty, prettyEra, prettyCountry, type QuizTarget } from '../App';
import type { CountryFilter, DifficultyFilter, EraFilter } from '../types';

type Props = {
  difficulty: DifficultyFilter;
  onChangeDifficulty: (d: DifficultyFilter) => void;
  era: EraFilter;
  onChangeEra: (e: EraFilter) => void;
  country: CountryFilter;
  onChangeCountry: (c: CountryFilter) => void;
  countFor: (target: QuizTarget) => number;
  onStartQuiz: (target: QuizTarget) => void;
};

const DIFFICULTIES: DifficultyFilter[] = ['mix', 'easy', 'medium', 'hard', 'very_hard'];
const ERAS: EraFilter[] = ['all', 'soviet', '1990s', '2000s', '2010s_plus'];
const COUNTRIES: CountryFilter[] = ['all', 'russia', 'ukraine', 'both'];

export function Home({
  difficulty,
  onChangeDifficulty,
  era,
  onChangeEra,
  country,
  onChangeCountry,
  countFor,
  onStartQuiz,
}: Props) {
  const allCount = countFor('all');

  return (
    <div className="container">
      <p className="home-kicker">Quiz Mode</p>
      <h1 className="home-heading">Review what you know.</h1>

      <div className="filter-group">
        <div className="filter-label">Difficulty</div>
        <div className="filter-tabs" role="tablist">
          {DIFFICULTIES.map((d) => (
            <button
              key={d}
              role="tab"
              aria-selected={difficulty === d}
              className={`filter-tab ${difficulty === d ? 'filter-tab-active' : ''}`}
              onClick={() => onChangeDifficulty(d)}
            >
              {prettyDifficulty[d]}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <div className="filter-label">Era</div>
        <div className="filter-tabs" role="tablist">
          {ERAS.map((e) => (
            <button
              key={e}
              role="tab"
              aria-selected={era === e}
              className={`filter-tab ${era === e ? 'filter-tab-active' : ''}`}
              onClick={() => onChangeEra(e)}
            >
              {prettyEra[e]}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <div className="filter-label">Country</div>
        <div className="filter-tabs" role="tablist">
          {COUNTRIES.map((c) => (
            <button
              key={c}
              role="tab"
              aria-selected={country === c}
              className={`filter-tab ${country === c ? 'filter-tab-active' : ''}`}
              onClick={() => onChangeCountry(c)}
            >
              {prettyCountry[c]}
            </button>
          ))}
        </div>
      </div>

      <button
        className="category-featured"
        onClick={() => onStartQuiz('all')}
        disabled={allCount === 0}
      >
        <p className="category-featured-kicker">Everything</p>
        <h2 className="category-featured-title">All Topics</h2>
        <p className="category-featured-meta">
          {allCount > 0
            ? `${allCount} questions`
            : 'No questions match these filters'}
        </p>
      </button>

      <p className="section-label">Browse by category</p>
      <div className="category-grid">
        {CATEGORIES.map((cat) => {
          const count = countFor(cat.key);
          const disabled = count === 0;
          return (
            <button
              key={cat.key}
              className="category-card"
              onClick={() => onStartQuiz(cat.key)}
              disabled={disabled}
              aria-disabled={disabled}
            >
              <div>
                <h2 className="category-card-title">{cat.name}</h2>
                <p className="category-card-meta">
                  {count > 0
                    ? `${count} questions · ${cat.description}`
                    : 'No questions match these filters'}
                </p>
              </div>
              <span className="category-card-arrow" aria-hidden>
                ▸
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
