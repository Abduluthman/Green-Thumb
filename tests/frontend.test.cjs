const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');

const script = fs.readFileSync('static/app.js', 'utf8');
const dictionary = JSON.parse(fs.readFileSync('dictionary.json', 'utf8'));
const dictionaryMarkup = '<input id="search-box"><select id="stream-filter"><option value=""></option><option value="e-waste"></option></select><select id="risk-filter"><option value=""></option><option value="special-handling"></option></select><p id="dictionary-status"></p><div id="waste-list"></div>';
const detailMarkup = '<h1 id="wasteName"></h1><p id="other-names"></p><p id="risk-level"></p><p id="waste-streams"></p><div id="risk-alert" hidden><strong id="risk-alert-title"></strong><p id="risk-alert-text"></p></div><p id="waste-description"></p><p id="proper-disposal"></p><p id="disposal-routes"></p><p id="precautions"></p><p id="guidance-note"></p><p id="reviewed-at"></p><ul id="source-list"></ul><p id="local-authority"></p><p id="local-contact"></p><a id="report-guidance"></a><div id="waste-details" hidden></div>';

async function setup(page, markup, data, path = '/') {
  const dom = new JSDOM(`<meta name="csrf-token" content="test-token"><main data-page="${page}">${markup}</main>`, {
    url: `https://green-thumb.test${path}`, runScripts: 'outside-only', pretendToBeVisual: true,
  });
  const calls = [];
  dom.window.fetch = async (url, options) => {
    calls.push({ url, options });
    if (data instanceof Error) throw data;
    return { ok: true, json: async () => data };
  };
  dom.window.eval(script + '\nwindow.showResult = showResult;');
  await new Promise(resolve => setImmediate(resolve));
  return { dom, document: dom.window.document, calls };
}

test('dictionary renders all entries and ranks an exact alias', async () => {
  const { dom, document } = await setup('dictionary', dictionaryMarkup, dictionary);
  assert.equal(document.querySelectorAll('.dictionary-item').length, 136);
  const input = document.getElementById('search-box');
  input.value = 'Tin Foil';
  input.dispatchEvent(new dom.window.Event('input'));
  assert.equal(document.querySelector('.dictionary-item strong').textContent, 'Aluminium Foil');
  input.value = 'no-such-item-12345';
  input.dispatchEvent(new dom.window.Event('input'));
  assert.equal(document.querySelectorAll('.dictionary-item').length, 0);
  assert.match(document.getElementById('dictionary-status').textContent, /No matches/);
  dom.window.close();
});

test('dictionary filters special handling and electronic waste', async () => {
  const { dom, document } = await setup('dictionary', dictionaryMarkup, dictionary);
  const risk = document.getElementById('risk-filter');
  risk.value = 'special-handling';
  risk.dispatchEvent(new dom.window.Event('change'));
  assert.equal(document.querySelectorAll('.dictionary-item').length, 22);
  assert.equal(document.querySelectorAll('.risk-chip.special-handling').length, 22);
  risk.value = '';
  const stream = document.getElementById('stream-filter');
  stream.value = 'e-waste';
  stream.dispatchEvent(new dom.window.Event('change'));
  assert.equal(document.querySelectorAll('.dictionary-item').length, 19);
  dom.window.close();
});

test('dictionary initialises from a refinement query', async () => {
  const { dom, document } = await setup('dictionary', dictionaryMarkup, dictionary, '/WasteDictionary.html?q=Plastic%20bottle');
  assert.equal(document.getElementById('search-box').value, 'Plastic bottle');
  assert.match(document.getElementById('waste-list').textContent, /Plastic/);
  dom.window.close();
});

test('detail page handles missing item parameter without throwing', async () => {
  const { dom, document } = await setup('detail', '<h1 id="wasteName"></h1>', dictionary, '/Search-Template.html');
  assert.match(document.getElementById('wasteName').textContent, /Item not found/);
  dom.window.close();
});

test('detail page resolves an entry and exposes evidence status', async () => {
  const { dom, document } = await setup('detail', detailMarkup, dictionary, '/Search-Template.html?item=Plastic');
  assert.equal(document.getElementById('wasteName').textContent, 'Plastic');
  assert.equal(document.getElementById('waste-details').hidden, false);
  assert.ok(document.getElementById('proper-disposal').textContent.length);
  assert.match(document.getElementById('guidance-note').textContent, /original project dictionary/);
  assert.match(document.getElementById('local-authority').textContent, /Abuja Environmental Protection Board/);
  assert.match(document.getElementById('report-guidance').href, /item=Plastic/);
  dom.window.close();
});

test('dictionary correction feedback is prefilled from its detail page', async () => {
  const markup = '<form id="feedbackForm"><select name="issue"><option value=""></option><option>Dictionary correction</option></select><textarea name="description"></textarea><button></button></form><p id="feedback-status"></p>';
  const { dom, document } = await setup('feedback', markup, [], '/Feedback.html?topic=Dictionary%20correction&item=Glass');
  assert.equal(document.querySelector('[name="issue"]').value, 'Dictionary correction');
  assert.match(document.querySelector('[name="description"]').value, /Dictionary item: Glass/);
  dom.window.close();
});

test('hazardous detail shows special handling and official sources', async () => {
  const { dom, document } = await setup('detail', detailMarkup, dictionary, '/Search-Template.html?item=Batteries');
  assert.equal(document.getElementById('risk-alert').hidden, false);
  assert.match(document.getElementById('risk-level').textContent, /Special handling/);
  assert.ok(document.querySelectorAll('#source-list a').length);
  dom.window.close();
});

test('admin feedback is rendered as literal text rather than executable markup', async () => {
  const attack = '<img src=x onerror=alert(1)>';
  const { dom, document } = await setup('admin', '<p id="admin-status"></p><div id="feedback-container"></div>', [
    { issue: attack, description: attack, timestamp: '2026-01-01T00:00:00Z' },
  ]);
  assert.equal(document.querySelectorAll('#feedback-container img').length, 0);
  assert.equal(document.querySelector('#feedback-container h2').textContent, attack);
  assert.equal(document.querySelector('#feedback-container p').textContent, attack);
  dom.window.close();
});

test('dictionary fetch failures are visible to the user', async () => {
  const { dom, document } = await setup('dictionary', dictionaryMarkup, new Error('Connection unavailable'));
  assert.equal(document.getElementById('dictionary-status').textContent, 'Connection unavailable');
  dom.window.close();
});

test('prediction uncertainty and optional refinement are handled separately', async () => {
  const markup = '<h2 id="result"></h2><p id="result-detail"></p><a id="search-link"></a><div id="refine-panel" hidden><div id="refine-options"></div></div>';
  const { dom, document } = await setup('', markup, []);
  dom.window.showResult({ class: 'Not Classified', confidence: 0.4 });
  assert.equal(document.getElementById('search-link').hidden, true);
  assert.equal(document.getElementById('refine-panel').hidden, true);
  dom.window.showResult({ class: 'Plastic', confidence: 0.9 });
  assert.equal(document.getElementById('search-link').hidden, false);
  assert.equal(document.getElementById('refine-panel').hidden, false);
  assert.equal(document.querySelectorAll('#refine-options a').length, 3);
  assert.match(document.querySelector('#refine-options a').href, /q=Plastic\+Bottles/);
  dom.window.close();
});

test('camera does not activate or transmit frames on page load', async () => {
  const { dom, document, calls } = await setup('camera', '<video id="video"></video><button id="start-camera"></button><button id="stop-camera" disabled></button><button id="capture" disabled></button><p id="camera-status"></p>', []);
  assert.equal(calls.length, 0);
  assert.equal(document.getElementById('video').srcObject, undefined);
  assert.equal(document.getElementById('capture').disabled, true);
  dom.window.close();
});
