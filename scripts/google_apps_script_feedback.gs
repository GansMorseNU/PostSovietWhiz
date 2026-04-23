const SHEET_NAME = 'Feedback';
const ANSWERS_SHEET_NAME = 'Answers';
const SESSIONS_SHEET_NAME = 'Sessions';
const READBACK_TOKEN = 'replace-with-a-long-random-secret';
const DEFAULT_READBACK_LIMIT = 100;

function doPost(e) {
  const payload = JSON.parse((e && e.postData && e.postData.contents) || '{}');

  if (payload.type === 'answer_event') {
    return handleAnswerEvent_(payload);
  }
  if (payload.type === 'session_start') {
    return handleSessionStart_(payload);
  }

  return handleFeedback_(payload);
}

function handleFeedback_(payload) {
  const sheet = getOrCreateSheet_();
  ensureHeaders_(sheet);

  sheet.appendRow([
    payload.submittedAt || '',
    payload.workflow || '',
    payload.autoApply || false,
    payload.kind || '',
    payload.questionId || '',
    payload.prompt || '',
    payload.category || '',
    payload.difficulty || '',
    payload.era || '',
    payload.country || '',
    payload.surface || '',
    payload.gameLevel ? `${payload.gameLevel.level} - ${payload.gameLevel.name}` : '',
    payload.selectedChoiceText || '',
    payload.wasCorrect === undefined ? '' : payload.wasCorrect,
    payload.details || '',
    payload.suggestedRewrite || '',
    payload.reporter || '',
    JSON.stringify(payload),
  ]);

  return ContentService.createTextOutput(
    JSON.stringify({ ok: true }),
  ).setMimeType(ContentService.MimeType.JSON);
}

function handleAnswerEvent_(payload) {
  const sheet = getOrCreateAnswersSheet_();
  ensureAnswerHeaders_(sheet);
  sheet.appendRow([
    payload.id || '',
    payload.submittedAt || '',
    payload.clientId || '',
    payload.sessionId || '',
    payload.questionId || '',
    payload.surface || '',
    payload.wasCorrect === undefined ? '' : payload.wasCorrect,
    payload.difficulty || '',
    payload.era || '',
    payload.country || '',
    payload.category || '',
  ]);
  return ContentService.createTextOutput(
    JSON.stringify({ ok: true }),
  ).setMimeType(ContentService.MimeType.JSON);
}

function handleSessionStart_(payload) {
  const sheet = getOrCreateSessionsSheet_();
  ensureSessionHeaders_(sheet);
  sheet.appendRow([
    payload.id || '',
    payload.submittedAt || '',
    payload.clientId || '',
    payload.sessionId || '',
    payload.appVersion || '',
    payload.surface || '',
  ]);
  return ContentService.createTextOutput(
    JSON.stringify({ ok: true }),
  ).setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  if (!isAuthorizedReadback_(e)) {
    return jsonResponse_({
      ok: false,
      error:
        'Unauthorized. Provide the correct token query parameter and set READBACK_TOKEN in the Apps Script project.',
    });
  }

  const kind = getParameter_(e, 'kind');
  if (kind === 'answer_stats') {
    return jsonResponse_(computeAnswerStats_());
  }
  if (kind === 'usage_stats') {
    return jsonResponse_(computeUsageStats_());
  }

  const rows = getFeedbackRows_();
  const workflow = getParameter_(e, 'workflow');
  const autoApplyOnly = getParameter_(e, 'auto_apply_only') === 'true';
  const questionId = getParameter_(e, 'question_id');
  const limit = clampLimit_(Number(getParameter_(e, 'limit')) || DEFAULT_READBACK_LIMIT);

  let filtered = rows;
  if (workflow) {
    filtered = filtered.filter((row) => row.workflow === workflow);
  }
  if (autoApplyOnly) {
    filtered = filtered.filter((row) => String(row.auto_apply).toLowerCase() === 'true');
  }
  if (questionId) {
    filtered = filtered.filter((row) => row.question_id === questionId);
  }

  const items = filtered.slice(-limit).reverse();
  return jsonResponse_({
    ok: true,
    count: items.length,
    items: items,
  });
}

function computeAnswerStats_() {
  const sheet = getOrCreateAnswersSheet_();
  ensureAnswerHeaders_(sheet);
  const values = sheet.getDataRange().getValues();
  if (values.length <= 1) return { ok: true, questions: [], total_events: 0 };

  const headers = values[0];
  const col = headerMap_(headers);
  const seenEventIds = Object.create(null);
  const byQuestion = Object.create(null);

  for (let i = 1; i < values.length; i++) {
    const row = values[i];
    const id = row[col.id];
    if (id && seenEventIds[id]) continue;
    if (id) seenEventIds[id] = true;

    const qid = row[col.question_id];
    if (!qid) continue;
    const rec = byQuestion[qid] || (byQuestion[qid] = { question_id: qid, seen: 0, correct: 0 });
    rec.seen++;
    if (String(row[col.was_correct]).toLowerCase() === 'true') rec.correct++;
  }

  const questions = Object.keys(byQuestion).map((qid) => {
    const rec = byQuestion[qid];
    return {
      question_id: qid,
      seen: rec.seen,
      correct: rec.correct,
      pct_correct: rec.seen > 0 ? Math.round((rec.correct / rec.seen) * 1000) / 10 : null,
    };
  });
  questions.sort((a, b) => b.seen - a.seen);

  return { ok: true, questions: questions, total_events: Object.keys(seenEventIds).length };
}

function computeUsageStats_() {
  const sheet = getOrCreateSessionsSheet_();
  ensureSessionHeaders_(sheet);
  const values = sheet.getDataRange().getValues();
  if (values.length <= 1) {
    return { ok: true, daily: [], monthly: [], total_launches: 0, total_clients: 0 };
  }

  const headers = values[0];
  const col = headerMap_(headers);
  const seenEventIds = Object.create(null);
  const daily = Object.create(null);
  const monthly = Object.create(null);
  const allClients = Object.create(null);

  for (let i = 1; i < values.length; i++) {
    const row = values[i];
    const id = row[col.id];
    if (id && seenEventIds[id]) continue;
    if (id) seenEventIds[id] = true;

    const submittedAt = row[col.submitted_at];
    const clientId = row[col.client_id];
    if (!submittedAt || !clientId) continue;

    const iso = String(submittedAt);
    const day = iso.slice(0, 10);
    const month = iso.slice(0, 7);

    const d = daily[day] || (daily[day] = { day: day, launches: 0, clients: Object.create(null) });
    d.launches++;
    d.clients[clientId] = true;

    const m = monthly[month] || (monthly[month] = { month: month, launches: 0, clients: Object.create(null) });
    m.launches++;
    m.clients[clientId] = true;

    allClients[clientId] = true;
  }

  const dailyOut = Object.keys(daily).sort().map((k) => ({
    day: daily[k].day,
    launches: daily[k].launches,
    unique_clients: Object.keys(daily[k].clients).length,
  }));
  const monthlyOut = Object.keys(monthly).sort().map((k) => ({
    month: monthly[k].month,
    launches: monthly[k].launches,
    unique_clients: Object.keys(monthly[k].clients).length,
  }));

  return {
    ok: true,
    daily: dailyOut,
    monthly: monthlyOut,
    total_launches: Object.keys(seenEventIds).length,
    total_clients: Object.keys(allClients).length,
  };
}

function headerMap_(headers) {
  const map = {};
  headers.forEach((h, i) => { map[h] = i; });
  return map;
}

function getOrCreateSheet_() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  return spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
}

function getOrCreateAnswersSheet_() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  return spreadsheet.getSheetByName(ANSWERS_SHEET_NAME) || spreadsheet.insertSheet(ANSWERS_SHEET_NAME);
}

function getOrCreateSessionsSheet_() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  return spreadsheet.getSheetByName(SESSIONS_SHEET_NAME) || spreadsheet.insertSheet(SESSIONS_SHEET_NAME);
}

function getFeedbackRows_() {
  const sheet = getOrCreateSheet_();
  ensureHeaders_(sheet);

  const values = sheet.getDataRange().getValues();
  if (values.length <= 1) return [];

  const headers = values[0];
  return values.slice(1).map((row) => {
    const item = {};
    headers.forEach((header, index) => {
      item[header] = row[index];
    });

    if (item.raw_json) {
      try {
        item.raw_json = JSON.parse(item.raw_json);
      } catch (err) {
        // Keep the raw string if parsing fails.
      }
    }

    return item;
  });
}

function ensureHeaders_(sheet) {
  if (sheet.getLastRow() > 0) return;

  sheet.appendRow([
    'submitted_at',
    'workflow',
    'auto_apply',
    'kind',
    'question_id',
    'prompt',
    'category',
    'difficulty',
    'era',
    'country',
    'surface',
    'game_level',
    'selected_choice_text',
    'was_correct',
    'details',
    'suggested_rewrite',
    'reporter',
    'raw_json',
  ]);
}

function ensureAnswerHeaders_(sheet) {
  if (sheet.getLastRow() > 0) return;
  sheet.appendRow([
    'id',
    'submitted_at',
    'client_id',
    'session_id',
    'question_id',
    'surface',
    'was_correct',
    'difficulty',
    'era',
    'country',
    'category',
  ]);
}

function ensureSessionHeaders_(sheet) {
  if (sheet.getLastRow() > 0) return;
  sheet.appendRow([
    'id',
    'submitted_at',
    'client_id',
    'session_id',
    'app_version',
    'surface',
  ]);
}

function isAuthorizedReadback_(e) {
  const token = getParameter_(e, 'token');
  if (!READBACK_TOKEN || READBACK_TOKEN === 'replace-with-a-long-random-secret') {
    return false;
  }
  return token === READBACK_TOKEN;
}

function getParameter_(e, key) {
  return (e && e.parameter && e.parameter[key]) || '';
}

function clampLimit_(value) {
  if (!value || isNaN(value)) return DEFAULT_READBACK_LIMIT;
  return Math.max(1, Math.min(500, value));
}

function jsonResponse_(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload, null, 2)).setMimeType(
    ContentService.MimeType.JSON,
  );
}
