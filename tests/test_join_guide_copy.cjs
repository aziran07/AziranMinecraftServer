const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadPage(clipboard) {
  let click;
  let selected;
  const address = { textContent: 'mc.aziran.uk', focus() {} };
  const status = { textContent: '', dataset: {} };
  const button = {
    dataset: { copyTarget: 'server-address' },
    focus() {},
    addEventListener(event, listener) {
      assert.equal(event, 'click');
      click = listener;
    },
  };
  const nodes = { 'copy-address': button, 'server-address': address, 'copy-status': status };
  const context = {
    navigator: { clipboard },
    console: { warn() {} },
    document: {
      getElementById(id) { return nodes[id]; },
      createRange() { return { selectNodeContents(node) { selected = node; } }; },
    },
    window: {
      getSelection() { return { removeAllRanges() {}, addRange() {} }; },
    },
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../site/app.js'), 'utf8'), context);
  return { click, status, address, selected: () => selected };
}

test('copy reports success only after clipboard write succeeds', async () => {
  let resolve;
  let copied;
  const page = loadPage({ writeText(text) {
    copied = text;
    return new Promise(done => { resolve = done; });
  } });
  page.click();
  assert.equal(copied, 'mc.aziran.uk');
  assert.equal(page.status.textContent, '');
  resolve();
  await new Promise(setImmediate);
  assert.equal(page.status.dataset.state, 'ok');
  assert.match(page.status.textContent, /mc\.aziran\.uk/);
});

test('denied clipboard access explains manual copy without claiming success', async () => {
  const page = loadPage({ async writeText() { throw new Error('Permission denied'); } });
  page.click();
  await new Promise(setImmediate);
  assert.equal(page.status.dataset.state, 'fail');
  assert.match(page.status.textContent, /Ctrl\+C/);
  assert.equal(page.selected(), page.address);
});
