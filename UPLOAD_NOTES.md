# 完整项目备份

此目录包含 aupet-new 的当前源代码、前端素材、项目文档，以及 aupet 的在线编程整合代码（前端 frontend/public/online-programming 与 OnlineProgrammingLesson.vue，后端 /api/student/ai/programming-tutor；原独立原型目录已并入后移除）。

数据库文件：

- database/current.sql：本次从正在运行的 MySQL 导出的完整数据库，含表结构、数据、触发器、事件和存储过程。
- init.sql 和原数据库目录：保留的原始数据库备份。

恢复当前数据库（在安装 MySQL 的电脑上）：

```powershell
mysql -u root -p -e "source database/current.sql"
```

复制 backend/config_local.example.py 为 backend/config_local.py，然后填入本地数据库密码和 DeepSeek 密钥。后端和前端启动方式参见 README.md。

项目所有者已明确确认公开上传完整数据库，其中包含账号、学生教师记录、评估信息和聊天记录。init.sql 与仓库原有数据库备份内容相同。未打包本地密钥、虚拟环境、node_modules、构建缓存或运行日志。原项目忽略的第三方模型目录与压缩包在本次源目录中不存在。
