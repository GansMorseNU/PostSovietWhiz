import { prettyCountry, prettyEra } from '../App';
import type { CountryFilter, EraFilter } from '../types';

type Props = {
  era: EraFilter;
  onChangeEra: (era: EraFilter) => void;
  country: CountryFilter;
  onChangeCountry: (country: CountryFilter) => void;
  matchingCount: number;
  onStartGame: () => void;
};

const ERAS: EraFilter[] = ['all', 'soviet', '1990s', '2000s', '2010s_plus'];
const COUNTRIES: CountryFilter[] = ['all', 'russia', 'ukraine', 'both'];

export function GameSetup({
  era,
  onChangeEra,
  country,
  onChangeCountry,
  matchingCount,
  onStartGame,
}: Props) {
  return (
    <div className="container container-with-bottom-bar">
      <p className="home-kicker">Game Mode</p>
      <h1 className="home-heading">Build your run.</h1>
      <p className="home-lede">
        Set filters before you start. They apply across every level of the game.
      </p>

      <div className="filter-group">
        <div className="filter-label">Era</div>
        <div className="filter-tabs" role="tablist">
          {ERAS.map((value) => (
            <button
              key={value}
              role="tab"
              aria-selected={era === value}
              className={`filter-tab ${era === value ? 'filter-tab-active' : ''}`}
              onClick={() => onChangeEra(value)}
            >
              {prettyEra[value]}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-group">
        <div className="filter-label">Country</div>
        <div className="filter-tabs" role="tablist">
          {COUNTRIES.map((value) => (
            <button
              key={value}
              role="tab"
              aria-selected={country === value}
              className={`filter-tab ${country === value ? 'filter-tab-active' : ''}`}
              onClick={() => onChangeCountry(value)}
            >
              {prettyCountry[value]}
            </button>
          ))}
        </div>
      </div>

      <div className="game-setup-summary">
        <p className="game-setup-kicker">Question pool</p>
        <h2 className="game-setup-title">
          {matchingCount > 0 ? `${matchingCount} questions` : 'No matching questions'}
        </h2>
        <p className="game-setup-meta">
          {matchingCount > 0
            ? 'Game mode will draw from this filtered pool at every level.'
            : 'Adjust the filters before starting.'}
        </p>
      </div>

      <div className="bottom-bar">
        <div className="bottom-bar-inner">
          <button
            className="primary primary-accent"
            onClick={onStartGame}
            disabled={matchingCount === 0}
          >
            Start game
          </button>
        </div>
      </div>
    </div>
  );
}
