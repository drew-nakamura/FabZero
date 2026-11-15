const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../web/progress.js'), 'utf8');

function fixture(response) {
  const nodes = new Map();
  const element = () => ({
    hidden: false, className: '', textContent: '', children: [],
    setAttribute(key, value) {this[key] = value;},
    replaceChildren(...children) {this.children = children;},
    querySelector(selector) {return nodes.get(selector);},
    classList: {values: new Set(), add(value) {this.values.add(value);}, remove(...values) {values.forEach(value => this.values.delete(value));}, toggle(value, force) {force ? this.values.add(value) : this.values.delete(value);}},
  });
  for (const selector of ['#tool-progress-title', '#tool-progress-status', '#tool-progress-stages', '#tool-progress-elapsed', '.tool-progress-track', '#tool-progress-hide']) nodes.set(selector, element());
  let panel;
  const document = {createElement: element, body: {appendChild(node) {panel = node;}}};
  const window = {fetch: async () => ({ok: response.ok, json: async () => response.body})};
  vm.runInNewContext(source, {document, window, Date, setInterval: () => 1, clearInterval() {}});
  return {panel, nodes, window};
}

test('ASIC generation shows expected checks without claiming live stage progress', async () => {
  const ui = fixture({ok: true, body: {correct: true, evidence: 'ai_generated_rtl', spec: {target: 'asic'}, synthesis_verified: true, synthesis: {correct: true, evidence: 'generic_synthesis'}}});
  const pending = ui.window.fetch('/api/generate-rtl', {method: 'POST', body: JSON.stringify({spec: {target: 'asic'}})});
  assert.equal(ui.panel.hidden, false);
  assert.equal(ui.panel['aria-busy'], 'true');
  assert.equal(ui.nodes.get('#tool-progress-stages').children.length, 4);
  assert.match(ui.nodes.get('#tool-progress-status').textContent, /individual progress is not reported/);
  const response = await pending;
  await response.json();
  assert.equal(ui.panel['aria-busy'], 'false');
  assert.equal(ui.panel.classList.values.has('complete'), true);
  assert.ok(ui.nodes.get('#tool-progress-stages').children.every(step => step.className === 'passed'));
});

test('a successful HTTP response without accepted netlist evidence remains unconfirmed', async () => {
  const ui = fixture({ok: true, body: {correct: true, evidence: 'ai_generated_rtl', spec: {target: 'asic'}}});
  const response = await ui.window.fetch('/api/generate-rtl', {method: 'POST', body: JSON.stringify({spec: {target: 'asic'}})});
  await response.json();
  assert.equal(ui.panel.classList.values.has('failed'), true);
  assert.ok(ui.nodes.get('#tool-progress-stages').children.every(step => step.className === 'unconfirmed'));
});
