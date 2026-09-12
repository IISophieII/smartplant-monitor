# V1 验证记录

验证日期：2026-09-12。执行者：Codex AI 协作代理；不代表用户已经亲自完成验收。

## 已实际完成

- Windows，Python 3.12.14，pytest：**6 passed**（3.88 秒）。
- Ruff 静态检查：通过。
- JavaScript 语法检查：通过。
- 独立 PyModbus 服务进程与 TCP 客户端读取四个寄存器，数值与量纲范围验证：通过。
- 启动真实 Uvicorn 服务，使用本机 Microsoft Edge 无头浏览器访问网页。
- 浏览器验证：实时数值出现、按钮切换渐进故障、等待状态进入异常、切回正常后温度恢复：通过。
- 390px 手机宽度无横向页面溢出，浏览器无 JavaScript 运行错误。
- 保存真实故障过程截图，并目视检查桌面布局。

首次 pytest 因系统临时目录无读取权限而出现 4 个 setup 错误。使用工作区中的独立 `--basetemp` 重跑后全部通过；未修改测试断言规避问题。

环境存在一个 Starlette 使用 AnyIO 弃用别名的 DeprecationWarning，测试通过；后续升级依赖时应处理。

## 尚未完成/不能据此声称

- 本机没有 Docker，未实际构建镜像或启动 Compose。
- 本机运行的是 Python 3.12；GitHub Actions 已在 Ubuntu 上完成 Python 3.12 和 3.13 两组检查，均通过。
- 项目已上传至 IISophieII/smartplant-monitor。自动测试记录：https://github.com/IISophieII/smartplant-monitor/actions/runs/34704636127 （代码提交 215976360fd0e1751809b73c4434198ec99e3286，2026-09-13 北京时间）。
- 未连接真实 PLC、真实电机或传感器；没有真实工业数据精度、误报率、性能基准或生产可靠性结论。

## 本地复查

```sh
pytest -q
ruff check .
```

若默认临时目录不可访问，可指定一个可写的新目录，例如 `pytest -q --basetemp=./work-test-temp`。pytest 会管理这个临时目录，不要指向已有重要文件的目录。

