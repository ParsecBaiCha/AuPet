const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { Worker: NodeWorker } = require('node:worker_threads');
const { execFileSync } = require('node:child_process');
const root = path.resolve(process.argv[2] || __dirname);
const read = name => fs.readFileSync(path.join(root, name), 'utf8');

function page(saved = '{}', Worker = BrowserWorker) {
  const elements = new Map();
  const element = id => {
    if (!elements.has(id)) elements.set(id, {
      value: '', textContent: '', style: {}, dataset: {}, classList: { toggle() {} },
      setAttribute() {}, addEventListener() {}, replaceChildren(...items) { this.children = items; },
      append(...items) { this.children = [...(this.children || []), ...items]; }
    });
    return elements.get(id);
  };
  const context = vm.createContext({
    document: { getElementById: element, querySelector: element, querySelectorAll: () => [], createElement: () => element(Symbol()) },
    localStorage: { getItem: () => saved, setItem() {} },
    location: { search: '' }, URLSearchParams, Blob, URL, Worker, setTimeout, clearTimeout, console
  });
  vm.runInContext(read('courses.js') + '\n' + read('app.js'), context);
  return { context, element };
}

// Run the actual browser JavaScript worker source in a separate thread.
class BrowserWorker {
  constructor(url) {
    this.terminated = false;
    this.ready = fetch(url).then(r => r.text()).then(source => {
      if (this.terminated) return;
      this.worker = new NodeWorker(`const {parentPort}=require('node:worker_threads');
        const self={postMessage:data=>parentPort.postMessage(data)};
        ${source}
        parentPort.on('message',data=>self.onmessage({data}));`, { eval: true });
      this.worker.on('message', data => this.onmessage?.({ data }));
      this.worker.on('error', error => this.onerror?.(error));
    });
  }
  postMessage(data) { this.ready.then(() => this.worker?.postMessage(data)); }
  terminate() { this.terminated = true; this.worker?.terminate(); }
}

async function main() {
  // Incorrect storage types must never prevent the lesson from opening.
  for (const saved of ['{"completed":{}}', '{"completed":"bad","drafts":"bad"}', 'null', 'invalid']) {
    const { context } = page(saved);
    assert.equal(vm.runInContext('completed.size', context), 0);
    assert.equal(vm.runInContext('typeof drafts', context), 'object');
  }
  const { context, element } = page();
  const catalog = vm.runInContext('courseCatalog', context);
  const execute = (code, input) => vm.runInContext('execute', context)(code, input);
  let wrapper;
  // Capture the exact Python wrapper without downloading Pyodide.
  const workerContext = vm.createContext({
    self: { postMessage() {} }, importScripts() { throw Error('skip'); }
  });
  vm.runInContext(read('python-worker.js'), workerContext);
  workerContext.fakePython = {
    toPy: () => ({ set() {}, get() {}, destroy() {} }),
    runPythonAsync: async source => { wrapper = source; }
  };
  vm.runInContext('py = fakePython', workerContext);
  await workerContext.self.onmessage({ data: { id: 1, code: '', input: '' } });
  const python = process.env.AUPET_PYTHON || path.join(process.env.AUPET_BACKEND || 'D:/GITHUB/aupet-new/backend', '.venv/Scripts/python.exe');
  function runPython(code, input) {
    const script = `import json,sys\n_student_code=${JSON.stringify(code)}\n_student_input=${JSON.stringify(input)}\n_original_stdin=sys.stdin\n${wrapper}\nassert sys.stdin is _original_stdin\nprint(json.dumps({'ok':_ok,'output':_result}))`;
    return JSON.parse(execFileSync(python, ['-B', '-X', 'utf8', '-c', script], { encoding: 'utf8', timeout: 5000 }));
  }
  const deepSolutions = [
    'console.log(x*w+b);', 'console.log(Math.max(0,z));',
    'for(const [p,a] of samples)sum+=(p-a)**2;console.log((sum/samples.length).toFixed(2));',
    'console.log(x1*w1+x2*w2+b>=0?1:0);'
  ];
  let count = 0;
  for (const [id, course] of Object.entries(catalog)) {
    vm.runInContext(`selectCourse(${JSON.stringify(id)})`, context);
    for (const [index, task] of course.tasks.entries()) {
      let code = task.starter;
      const solution = task.solution || deepSolutions[index];
      const marker = code.indexOf('console.log(');
      code = marker < 0 ? code + '\n' + solution : code.slice(0, marker) + solution + '\n' + code.slice(marker);
      for (const [input, expected] of task.tests) {
        const result = course.language === 'Python' ? runPython(code, input) : await execute(code, input);
        assert.equal(result.ok, true, `${course.title}/${task.name}: ${result.output}`);
        assert.equal(result.output.trim(), expected, `${course.title}/${task.name}`);
        count++;
      }
    }
  }
  vm.runInContext("selectCourse('deep')", context);
  assert.equal((await execute('console.log("a");console.log("b");', '')).output, 'a\nb');
  assert.equal((await execute('const = ;', '')).ok, false);
  assert.match((await execute('while(true){}', '')).output, /超过 2 秒/);
  assert.equal((await execute('console.log(7)', '')).output, '7');
  element('code').value = 'console.log(7)';
  element('input').value = '3 2 1';
  await vm.runInContext('run()', context);
  assert.equal(element('run').disabled, false);
  assert.match(element('test-result').children[0].textContent, /测试通过 1 \/ 3/);
  for (const code of [
    'import sys\nprint(sys.stdin.read(), end="")',
    'import sys\nprint(input())\nprint(sys.stdin.readline(), end="")'
  ]) assert.equal(runPython(code, 'first\nsecond\n').output, 'first\nsecond');
  assert.equal(runPython('raise ValueError("bad")', '').ok, false);
  assert.equal(runPython('input()', '').ok, false);

  // A blocked worker constructor must be retryable, with no stuck rejected promise.
  let attempts = 0;
  class BlockedWorker { constructor() { attempts++; throw Error('blocked'); } }
  const runtime = page('{}', BlockedWorker).context;
  vm.runInContext(read('python-runtime.js'), runtime);
  for (let i = 0; i < 2; i++) {
    const result = await vm.runInContext("executePython('print(1)', '')", runtime);
    assert.equal(result.ok, false);
    assert.match(result.output, /Python/);
  }
  assert.equal(attempts, 2);
  let loadAttempts = 0;
  class FailedLoadWorker {
    constructor() {
      loadAttempts++;
      setTimeout(() => this.onmessage?.({ data: { loadError: 'Python load failed' } }), 0);
    }
    terminate() {}
  }
  const failedLoad = page('{}', FailedLoadWorker).context;
  vm.runInContext(read('python-runtime.js'), failedLoad);
  for (let i = 0; i < 2; i++) {
    assert.equal((await vm.runInContext("executePython('print(1)', '')", failedLoad)).ok, false);
  }
  assert.equal(loadAttempts, 2);
  console.log(`${count} course cases passed; storage, worker retry, JS timeout/recovery, Python stdin/error checks passed`);
}
main().catch(error => { console.error(error); process.exitCode = 1; });
