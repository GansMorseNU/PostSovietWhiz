import type { Question } from './types';

// Flip this to true only AFTER the updated Apps Script (with the
// answer_event / session_start dispatch branches) has been redeployed.
// While false, logAnswer / logSessionStart are no-ops and nothing is
// queued or sent. Safe to ship to users with the flag off.
export const ANALYTICS_ENABLED = true;

const ENDPOINT =
  'https://script.google.com/macros/s/AKfycbwayTJFG-d5Nzz7YfBlYUfiOapNbGV0rNvvD_yYMYCBEcFF2uzHbZxYIKgGTDZ8rU5w/exec';
const ANALYTICS_QUEUE_KEY = 'post-soviet-whiz-analytics-queue';
const CLIENT_ID_KEY = 'post-soviet-whiz-client-id';
const SESSION_ID_KEY = 'post-soviet-whiz-session-id';
const MAX_QUEUE = 1000;

type AnalyticsEvent =
  | {
      type: 'answer_event';
      id: string;
      submittedAt: string;
      clientId: string;
      sessionId: string;
      questionId: string;
      surface: string;
      wasCorrect: boolean;
      difficulty: string;
      era: string;
      country: string;
      category: string;
    }
  | {
      type: 'session_start';
      id: string;
      submittedAt: string;
      clientId: string;
      sessionId: string;
      appVersion: string;
      surface: string;
    };

function uuid(): string {
  return globalThis.crypto?.randomUUID?.() ?? `id-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function getOrCreate(key: string): string {
  try {
    const existing = window.localStorage.getItem(key);
    if (existing) return existing;
    const fresh = uuid();
    window.localStorage.setItem(key, fresh);
    return fresh;
  } catch {
    return uuid();
  }
}

export function getClientId(): string {
  return getOrCreate(CLIENT_ID_KEY);
}

function getSessionId(): string {
  try {
    const existing = window.sessionStorage.getItem(SESSION_ID_KEY);
    if (existing) return existing;
    const fresh = uuid();
    window.sessionStorage.setItem(SESSION_ID_KEY, fresh);
    return fresh;
  } catch {
    return uuid();
  }
}

function readQueue(): AnalyticsEvent[] {
  try {
    const raw = window.localStorage.getItem(ANALYTICS_QUEUE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeQueue(queue: AnalyticsEvent[]): void {
  try {
    const capped = queue.length > MAX_QUEUE ? queue.slice(-MAX_QUEUE) : queue;
    window.localStorage.setItem(ANALYTICS_QUEUE_KEY, JSON.stringify(capped));
  } catch {
    // ignore storage errors
  }
}

function enqueue(event: AnalyticsEvent): void {
  const queue = readQueue();
  queue.push(event);
  writeQueue(queue);
}

function removeById(id: string): void {
  const queue = readQueue().filter((e) => e.id !== id);
  writeQueue(queue);
}

async function postEvent(event: AnalyticsEvent): Promise<boolean> {
  try {
    await fetch(ENDPOINT, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(event),
    });
    return true;
  } catch {
    return false;
  }
}

async function sendOrQueue(event: AnalyticsEvent): Promise<void> {
  const ok = await postEvent(event);
  if (!ok) enqueue(event);
}

export function logSessionStart(appVersion: string = ''): void {
  if (!ANALYTICS_ENABLED) return;
  const event: AnalyticsEvent = {
    type: 'session_start',
    id: uuid(),
    submittedAt: new Date().toISOString(),
    clientId: getClientId(),
    sessionId: getSessionId(),
    appVersion,
    surface: 'app_launch',
  };
  void sendOrQueue(event);
}

export function logAnswer(question: Question, wasCorrect: boolean, surface: string): void {
  if (!ANALYTICS_ENABLED) return;
  const event: AnalyticsEvent = {
    type: 'answer_event',
    id: uuid(),
    submittedAt: new Date().toISOString(),
    clientId: getClientId(),
    sessionId: getSessionId(),
    questionId: question.id,
    surface,
    wasCorrect,
    difficulty: question.difficulty,
    era: question.era,
    country: question.country,
    category: question.category,
  };
  void sendOrQueue(event);
}

let retryInFlight = false;

export async function retryPendingAnalytics(): Promise<number> {
  if (!ANALYTICS_ENABLED) return 0;
  if (retryInFlight) return 0;
  const queue = readQueue();
  if (queue.length === 0) return 0;

  retryInFlight = true;
  let sent = 0;
  try {
    for (const event of queue) {
      const ok = await postEvent(event);
      if (!ok) break;
      removeById(event.id);
      sent++;
    }
  } finally {
    retryInFlight = false;
  }
  return sent;
}
