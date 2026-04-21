import { APP_NAME } from '../App';
import { InstallPrompt } from './InstallPrompt';

type Props = {
  onQuizMode: () => void;
  onGameMode: () => void;
};

export function Start({ onQuizMode, onGameMode }: Props) {
  return (
    <div className="container start-container">
      <div className="start-hero">
        <h1 className="start-title">{APP_NAME}</h1>
        <p className="start-tagline">
          Review key concepts from Post-Soviet Politics: Russia, Ukraine, and
          the Road to War.
        </p>
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

      <p className="start-footer">
        PS369 · Northwestern University · Spring 2026
      </p>
    </div>
  );
}
