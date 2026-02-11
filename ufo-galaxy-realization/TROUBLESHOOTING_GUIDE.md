# UFO Galaxy 故障排查指南

**版本**: 1.0.0  
**最后更新**: 2026-02-11  

---

## 📚 目录

1. [常见问题](#常见问题)
2. [启动问题](#启动问题)
3. [节点问题](#节点问题)
4. [性能问题](#性能问题)
5. [网络问题](#网络问题)
6. [数据问题](#数据问题)
7. [日志分析](#日志分析)

---

## 常见问题

### 问题 1: 系统无法启动

**症状**: 运行 `python main_fixed.py` 后立即退出

**可能原因**:
- Python 版本不符合要求
- 缺少依赖库
- 配置文件格式错误
- 端口被占用

**解决方案**:

```bash
# 1. 检查 Python 版本
python --version  # 应该是 3.8+

# 2. 检查依赖
pip list | grep -E "requests|pyyaml|aiohttp"

# 3. 验证配置
python config_validator.py

# 4. 检查端口
lsof -i :8000  # 检查 8000 端口

# 5. 查看详细错误
python main_fixed.py --verbose
```

### 问题 2: 节点无法加载

**症状**: 某些节点显示 "failed" 或 "timeout" 状态

**可能原因**:
- 节点配置错误
- 节点依赖未满足
- 节点代码有 bug
- 资源不足

**解决方案**:

```bash
# 1. 检查节点配置
python config_validator.py

# 2. 查看节点日志
tail -f logs/nodes.log | grep "Node_XX"

# 3. 检查节点依赖
python -c "import json; config = json.load(open('node_dependencies.json')); print(config['nodes']['Node_XX'])"

# 4. 手动测试节点
cd nodes/Node_XX_YourNode
python main.py
```

### 问题 3: 端口被占用

**症状**: "Address already in use" 错误

**可能原因**:
- 上一个进程未完全关闭
- 其他应用占用了端口
- 系统端口配置冲突

**解决方案**:

```bash
# 1. 查找占用端口的进程
lsof -i :8000  # 查找占用 8000 端口的进程

# 2. 杀死进程
kill -9 <PID>

# 3. 修改端口配置
# 编辑 config.yaml，改变端口号

# 4. 重启系统
python main_fixed.py
```

### 问题 4: API 密钥无效

**症状**: API 调用返回 401 或 403 错误

**可能原因**:
- API 密钥过期
- API 密钥格式错误
- API 密钥权限不足
- 密钥未正确加载

**解决方案**:

```bash
# 1. 检查 .env 文件
cat .env | grep API_KEY

# 2. 验证密钥格式
# 检查密钥是否以正确的前缀开头（如 sk- 或 gsk-）

# 3. 测试 API 连接
python -c "from core.api_routes import test_api_connection; test_api_connection()"

# 4. 重新加载配置
# 重启系统
```

---

## 启动问题

### 启动超时

**症状**: 系统启动超过 5 分钟还未完成

**解决方案**:

```bash
# 1. 检查系统资源
top  # 查看 CPU 和内存使用

# 2. 检查网络连接
ping -c 1 8.8.8.8

# 3. 查看启动日志
tail -100 logs/system.log

# 4. 尝试最小化启动
python main_fixed.py --mode minimal
```

### 启动失败

**症状**: 启动过程中出现错误

**解决方案**:

```bash
# 1. 运行诊断
python config_validator.py

# 2. 运行自动修复
python auto_fix.py

# 3. 查看详细错误
python main_fixed.py --debug

# 4. 检查日志
grep "ERROR" logs/*.log
```

---

## 节点问题

### 节点崩溃

**症状**: 节点运行一段时间后停止响应

**解决方案**:

```bash
# 1. 检查节点日志
tail -f logs/nodes.log

# 2. 检查系统资源
top -p <node_pid>

# 3. 查看节点内存使用
ps aux | grep Node_

# 4. 重启节点
# 系统会自动重启失败的节点
```

### 节点依赖错误

**症状**: "Dependency not found" 错误

**解决方案**:

```bash
# 1. 检查依赖配置
python config_validator.py

# 2. 验证依赖节点是否运行
curl http://localhost:8001/health  # 检查 Node_01

# 3. 查看依赖关系
python -c "import json; config = json.load(open('node_dependencies.json')); print(json.dumps(config['nodes']['Node_XX'], indent=2))"

# 4. 修复依赖
python auto_fix.py
```

### 节点通信失败

**症状**: 节点间通信超时或失败

**解决方案**:

```bash
# 1. 检查网络连接
ping localhost

# 2. 检查端口是否开放
netstat -an | grep 8000

# 3. 查看通信日志
tail -f logs/node_communication.log

# 4. 测试直接通信
curl http://localhost:8000/api/v1/status
```

---

## 性能问题

### 系统响应缓慢

**症状**: API 响应时间过长（> 5 秒）

**解决方案**:

```bash
# 1. 检查 CPU 使用
top

# 2. 检查内存使用
free -h

# 3. 检查磁盘 I/O
iostat -x 1

# 4. 分析性能
python -m cProfile main_fixed.py
```

### 内存泄漏

**症状**: 内存使用持续增长

**解决方案**:

```bash
# 1. 监控内存
watch -n 1 'free -h'

# 2. 查看进程内存
ps aux --sort=-%mem | head

# 3. 使用内存分析工具
pip install memory-profiler
python -m memory_profiler main_fixed.py

# 4. 检查日志中的内存警告
grep "memory" logs/*.log
```

### 高 CPU 使用

**症状**: CPU 使用率持续 > 80%

**解决方案**:

```bash
# 1. 查看哪个进程占用 CPU
top

# 2. 查看进程中的线程
ps -eLf | grep python

# 3. 分析 CPU 使用
python -m cProfile -s cumulative main_fixed.py

# 4. 检查是否有无限循环
grep -n "while True" core/*.py
```

---

## 网络问题

### 无法连接到外部 API

**症状**: "Connection refused" 或 "Timeout" 错误

**解决方案**:

```bash
# 1. 检查网络连接
ping 8.8.8.8

# 2. 检查 DNS
nslookup api.openai.com

# 3. 检查防火墙
sudo ufw status

# 4. 测试 API 端点
curl -v https://api.openai.com/v1/models
```

### WebSocket 连接失败

**症状**: WebSocket 连接无法建立

**解决方案**:

```bash
# 1. 检查 WebSocket 端口
netstat -an | grep 8080

# 2. 查看 WebSocket 日志
tail -f logs/websocket.log

# 3. 测试 WebSocket 连接
python -c "
import websocket
ws = websocket.create_connection('ws://localhost:8080/ws')
print(ws.recv())
"

# 4. 检查防火墙设置
sudo ufw allow 8080
```

---

## 数据问题

### 数据库连接失败

**症状**: "Database connection refused" 错误

**解决方案**:

```bash
# 1. 检查数据库状态
ps aux | grep sqlite

# 2. 检查数据库文件
ls -la data/

# 3. 验证数据库完整性
sqlite3 data/galaxy.db "SELECT COUNT(*) FROM sqlite_master;"

# 4. 重建数据库
rm data/galaxy.db
python main_fixed.py  # 会自动创建新数据库
```

### 数据损坏

**症状**: 数据库查询返回错误

**解决方案**:

```bash
# 1. 备份数据
cp data/galaxy.db data/galaxy.db.backup

# 2. 检查数据库完整性
sqlite3 data/galaxy.db "PRAGMA integrity_check;"

# 3. 修复数据库
sqlite3 data/galaxy.db "VACUUM;"

# 4. 恢复备份
cp data/galaxy.db.backup data/galaxy.db
```

---

## 日志分析

### 查看系统日志

```bash
# 实时查看
tail -f logs/system.log

# 查看最后 100 行
tail -100 logs/system.log

# 搜索特定错误
grep "ERROR" logs/system.log

# 统计错误数量
grep "ERROR" logs/system.log | wc -l
```

### 查看节点日志

```bash
# 查看特定节点的日志
grep "Node_01" logs/nodes.log

# 查看节点启动日志
grep "Node_01" logs/system.log | grep "startup"
```

### 查看 API 日志

```bash
# 查看 API 请求
tail -f logs/api.log

# 查看 API 错误
grep "ERROR" logs/api.log

# 查看特定端点的日志
grep "/api/v1/nodes" logs/api.log
```

---

## 获取帮助

如果以上解决方案都不能解决问题，请：

1. 收集日志文件
2. 运行诊断脚本
3. 提交 Issue 到 GitHub

```bash
# 收集诊断信息
python config_validator.py > diagnostic_report.txt
python code_quality_audit.py >> diagnostic_report.txt
tail -100 logs/*.log >> diagnostic_report.txt
```

---

**最后更新**: 2026-02-11  
**维护者**: UFO Galaxy Team
