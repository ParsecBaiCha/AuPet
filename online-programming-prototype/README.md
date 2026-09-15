# 在线编程原型

启动：`npm start`，打开 http://127.0.0.1:4173 。

AI 复用 D:/GITHUB/aupet-new/backend/llm_service.py 的 DeepSeek 调用和已有 config_local.py 配置，不复制密钥。通过原项目 .venv/Scripts/python.exe 执行 ai_bridge.py。可用 AUPET_BACKEND 环境变量指定原项目 backend 路径。

此服务仅监听本机地址。聊天按任务保存在当前页面内存，发送最近对话、题目、代码、输入与运行结果；不写入原项目聊天数据库。关闭或刷新页面会清除提问记录。

原项目代码未修改。正式整合时应接入原项目登录和服务端权限体系。

现有五门课程均支持独立练习、代码保存和完成进度。新增四门课程的题目用例可运行 `node verify-courses.cjs` 验证（Python参考答案使用原项目虚拟环境运行）。Python学生代码由浏览器 Web Worker 内的 Pyodide 0.29.3 执行，首次使用需联网下载运行时，不在本机服务端执行学生代码。

运行 `npm test` 可验证五门课程的全部 63 个题目用例，以及保存数据损坏、JavaScript 多行输出/语法错误/死循环恢复、Python 标准输入/异常和 Worker 启动失败重试。JavaScript 使用实际 Worker 源码在独立线程运行；Python 使用实际执行包装代码在本机 Python 中验证，浏览器 Pyodide 仍需另行测试。可通过 `AUPET_PYTHON` 指定 Python 可执行文件，或通过 `AUPET_BACKEND` 指定后端目录。集成版可运行 `node verify-runtime.cjs integration/public/online-programming`。
