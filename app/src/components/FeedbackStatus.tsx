import { useEffect, useState } from 'react';
import {
  clearPendingFeedback,
  downloadPendingFeedback,
  getPendingFeedbackCount,
  isFeedbackEndpointConfigured,
  subscribeToFeedbackQueueChange,
} from '../feedback';

export function FeedbackStatus() {
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const sync = () => setPendingCount(getPendingFeedbackCount());
    sync();
    return subscribeToFeedbackQueueChange(sync);
  }, []);

  if (pendingCount === 0) return null;

  const endpointConfigured = isFeedbackEndpointConfigured();

  return (
    <div className="feedback-status-card">
      <p className="feedback-status-kicker">Saved feedback</p>
      <h2 className="feedback-status-title">
        {pendingCount} report{pendingCount === 1 ? '' : 's'} saved on this device
      </h2>
      <p className="feedback-status-copy">
        {endpointConfigured
          ? 'These are still queued locally on this device.'
          : 'Google Sheets sync is not configured yet, so feedback is being saved locally.'}
      </p>
      <div className="feedback-status-actions">
        <button className="primary primary-accent" onClick={downloadPendingFeedback}>
          Download JSON
        </button>
        <button className="ghost" onClick={clearPendingFeedback}>
          Clear saved reports
        </button>
      </div>
    </div>
  );
}
