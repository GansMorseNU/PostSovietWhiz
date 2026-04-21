# Google Apps Script feedback script

Overwrite the entire Apps Script editor contents with the script below, then:

1. Change `READBACK_TOKEN` to your real private secret.
2. Save.
3. Go to **Deploy -> Manage deployments -> Edit -> Deploy**.

```javascript
const SHEET_NAME = 'Feedback';
const READBACK_TOKEN = 'replace-with-a-long-random-secret';
const DEFAULT_READBACK_LIMIT = 100;

function doPost(e) {
  const sheet = getOrCreateSheet_();
  ensureHeaders_(sheet);

  const payload = JSON.parse((e && e.postData && e.postData.contents) || '{}');
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

function doGet(e) {
  if (!isAuthorizedReadback_(e)) {
    return jsonResponse_({
      ok: false,
      error:
        'Unauthorized. Provide the correct token query parameter and set READBACK_TOKEN in the Apps Script project.',
    });
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

function getOrCreateSheet_() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  return spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
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
```
