const SHEET_NAME = 'Feedback';

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

function getOrCreateSheet_() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  return spreadsheet.getSheetByName(SHEET_NAME) || spreadsheet.insertSheet(SHEET_NAME);
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
