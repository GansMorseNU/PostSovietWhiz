import { FeedbackStatus } from './FeedbackStatus';
import { InstallPrompt } from './InstallPrompt';
import heroBandImg from '../assets/hero-band.jpg';

type Props = {
  onQuizMode: () => void;
  onGameMode: () => void;
};

export function Start({ onQuizMode, onGameMode }: Props) {
  return (
    <div className="container start-container">
      <div
        className="start-hero-band"
        role="img"
        aria-label="Hammer and sickle on a cracked concrete wall"
        style={{ backgroundImage: `url(${heroBandImg})` }}
      />

      <div className="start-hero">
        <h1 className="start-title">
          <span className="start-title-line">Post-Soviet</span>
          <span className="start-title-line">Whiz</span>
        </h1>
      </div>

      <div className="start-modes">
        <button className="start-mode-card start-mode-quiz" onClick={onQuizMode}>
          <span className="start-mode-icon">📚</span>
          <div className="start-mode-body">
            <h2 className="start-mode-title">Quiz Mode</h2>
            <p className="start-mode-desc">
              Pick a topic and difficulty. Learn at your own pace.
            </p>
          </div>
          <span className="start-mode-arrow" aria-hidden>›</span>
        </button>

        <button className="start-mode-card start-mode-game" onClick={onGameMode}>
          <span className="start-mode-icon">🎮</span>
          <div className="start-mode-body">
            <h2 className="start-mode-title">Game Mode</h2>
            <p className="start-mode-desc">
              7 levels of rising difficulty. Score 8 / 10 to advance.
            </p>
          </div>
          <span className="start-mode-arrow" aria-hidden>›</span>
        </button>
      </div>

      <InstallPrompt />
      <FeedbackStatus />

      <p className="start-footer">
        PS369 · Northwestern University · Spring 2026
      </p>
    </div>
  );
}
