let py;
(async()=>{try{importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js');py=await loadPyodide();self.postMessage({ready:true});}catch{self.postMessage({loadError:'Python 环境加载失败，请检查网络并重试。'});}})();
self.onmessage=async({data})=>{const globals=py.toPy({});try{globals.set('_student_code',data.code);globals.set('_student_input',data.input);await py.runPythonAsync(`import io, sys, contextlib, traceback
_stream = io.StringIO(_student_input)
_out = io.StringIO()
def _read_input(prompt=''):
    line = _stream.readline()
    if line == '':
        raise EOFError('输入数据不足，请检查自定义输入')
    return line.rstrip('\\n')
_previous_stdin = sys.stdin
try:
    sys.stdin = _stream
    with contextlib.redirect_stdout(_out):
        exec(_student_code, {'input': _read_input, '__name__': '__main__'})
    _ok = True
    _result = _out.getvalue().rstrip('\\n')
except Exception:
    _ok = False
    _result = traceback.format_exc()
finally:
    sys.stdin = _previous_stdin
`,{globals});self.postMessage({id:data.id,ok:globals.get('_ok'),output:globals.get('_result')});}catch(e){self.postMessage({id:data.id,ok:false,output:e.message});}finally{globals.destroy();}};
