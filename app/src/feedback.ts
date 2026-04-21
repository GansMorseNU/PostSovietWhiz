import type { Question } from './types';

export type FeedbackKind =
  | 'fact_error'
  | 'reword'
  | 'difficulty'
  | 'distractors'
  | 'game_level'
  | 'bug'
  | 'other';

export type FeedbackSurface =
  | 'quiz'
  | 'game'
  | 'quiz_results'
  | 'game_results';

export type FeedbackContext = {
  surface: FeedbackSurface;
  questionPosition?: {
    current: number;
    total: number;
  };
  selectedChoiceText?: string;
  wasCorrect?: boolean;
  gameLevel?: {
    level: number;
    name: string;
  };
};

export type FeedbackSubmission = {
  id: string;
  submittedAt: string;
  workflow: 'auto_apply_next_pass' | 'review_queue';
  autoApply: boolean;
  kind: FeedbackKind;
  details: string;
  suggestedRewrite?: string;
  reporter?: string;
  questionId: string;
  prompt: string;
  difficulty: string;
  era: string;
  country: string;
  category: string;
  surface: FeedbackSurface;
  questionPosition?: FeedbackContext['questionPosition'];
  selectedChoiceText?: string;
  wasCorrect?: boolean;
  gameLevel?: FeedbackContext['gameLevel'];
};

type SubmitFeedbackInput = {
  question: Question;
  context: FeedbackContext;
  kind: FeedbackKind;
  details: string;
  suggestedRewrite?: string;
  reporter?: string;
};

export type SubmitFeedbackResult = {
  destination: 'remote' | 'local';
  message: string;
  pendingCount: number;
};

const DEFAULT_FEEDBACK_ENDPOINT = '';
const FEEDBACK_QUEUE_KEY = 'post-soviet-whiz-feedback-queue';
const FEEDBACK_QUEUE_EVENT = 'post-soviet-whiz-feedback-queue-change';

function dispatchQueueEvent() {
  window.dispatchEvent(new Event(FEEDBACK_QUEUE_EVENT));
}

function buildSubmission(input: SubmitFeedbackInput): FeedbackSubmission {
  const textToInspect = [input.details, input.suggestedRewrite, input.reporter]
    .filter(Boolean)
    .join('\n');
  const autoApply = textToInspect.includes('*JGM*');

  return {
    id: globalThis.crypto?.randomUUID?.() ?? `fb-${Date.now()}`,
    submittedAt: new Date().toISOString(),
    workflow: autoApply ? 'auto_apply_next_pass' : 'review_queue',
    autoApply,
    kind: input.kind,
    details: input.details,
    suggestedRewrite: input.suggestedRewrite || undefined,
    reporter: input.reporter || undefined,
    questionId: input.question.id,
    prompt: input.question.prompt,
    difficulty: input.question.difficulty,
    era: input.question.era,
    country: input.question.country,
    category: input.question.category,
    surface: input.context.surface,
    questionPosition: input.context.questionPosition,
    selectedChoiceText: input.context.selectedChoiceText,
    wasCorrect: input.context.wasCorrect,
    gameLevel: input.context.gameLevel,
  };
}

export function getFeedbackEndpoint(): string {
  return DEFAULT_FEEDBACK_ENDPOINT.trim();
}

export function isFeedbackEndpointConfigured(): boolean {
  return getFeedbackEndpoint().length > 0;
}

export function getPendingFeedback(): FeedbackSubmission[] {
  const raw = window.localStorage.getItem(FEEDBACK_QUEUE_KEY);
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function savePendingFeedback(submission: FeedbackSubmission): number {
  const pending = getPendingFeedback();
  pending.push(submission);
  window.localStorage.setItem(FEEDBACK_QUEUE_KEY, JSON.stringify(pending));
  dispatchQueueEvent();
  return pending.length;
}

export function getPendingFeedbackCount(): number {
  return getPendingFeedback().length;
}

export function clearPendingFeedback() {
  window.localStorage.removeItem(FEEDBACK_QUEUE_KEY);
  dispatchQueueEvent();
}

export function downloadPendingFeedback(): boolean {
  const pending = getPendingFeedback();
  if (pending.length === 0) return false;

  const blob = new Blob([JSON.stringify(pending, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `post-soviet-whiz-feedback-${new Date()
    .toISOString()
    .slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(url);
  return true;
}

export function subscribeToFeedbackQueueChange(callback: () => void): () => void {
  window.addEventListener(FEEDBACK_QUEUE_EVENT, callback);
  return () => window.removeEventListener(FEEDBACK_QUEUE_EVENT, callback);
}

export async function submitFeedback(
  input: SubmitFeedbackInput,
): Promise<SubmitFeedbackResult> {
  const submission = buildSubmission(input);
  const endpoint = getFeedbackEndpoint();

  if (!endpoint) {
    const pendingCount = savePendingFeedback(submission);
    return {
      destination: 'local',
      pendingCount,
      message:
        'Feedback saved on this device. Once Google Sheets sync is configured, future reports can be sent centrally.',
    };
  }

  try {
    await fetch(endpoint, {
      method: 'POST',
      mode: 'no-cors',
      headers: {
        'Content-Type': 'text/plain;charset=utf-8',
      },
      body: JSON.stringify(submission),
    });

    return {
      destination: 'remote',
      pendingCount: getPendingFeedbackCount(),
      message: 'Feedback sent. Thanks.',
    };
  } catch {
    const pendingCount = savePendingFeedback(submission);
    return {
      destination: 'local',
      pendingCount,
      message:
        'The feedback endpoint could not be reached, so this report was saved on this device instead.',
    };
  }
}
