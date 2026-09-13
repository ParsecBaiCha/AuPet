const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

async function main() {
  for (const file of ['tutor.js', 'integration/public/online-programming/tutor.js']) {
    const source = fs.readFileSync(file, 'utf8');
    const read = vm.runInNewContext(source.slice(0, source.indexOf('const tutorDialog')) + ';readTutorResponse');
    assert.equal((await read({ ok: true, json: async () => ({ answer: 'test' }) })).answer, 'test');
    for (const [status, message] of [[401, /重新登录/], [403, /学生账户/], [404, /重启后端/], [502, /无法响应/], [503, /尚未配置/]]) {
      for (const json of [async () => ({}), async () => { throw Error('HTML response'); }]) {
        await assert.rejects(() => read({ ok: false, status, json }), message);
      }
    }
    await assert.rejects(() => read({ ok: true, json: async () => null }), /无效数据/);
    await assert.rejects(() => read({ ok: false, status: 429, json: async () => ({ error: 'too many requests' }) }), /too many requests/);
  }
  console.log('Tutor response checks passed for standalone and integrated modules');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
