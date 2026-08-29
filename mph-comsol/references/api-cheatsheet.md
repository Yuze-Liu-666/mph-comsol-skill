# MPh 公开 API 速查

> 依据 MPh v1.3.2 源码（`mph/__init__.py`、`session.py`、`client.py`、`model.py`、`node.py`、`config.py`、`server.py`）整理。
> 完整签名以 https://mph.readthedocs.io 的 API 页为准。

## 顶层入口（mph/__init__.py）

```python
mph.start(cores=None, version=None)   # 启动 COMSOL 服务器，返回 Client
mph.option(name=None, value=None)     # 读写配置；name 省略 = 全部选项
mph.Client / mph.Server / mph.Model / mph.Node
mph.tree(model, max_depth=None)       # 打印模型树（树形字符图）
mph.inspect(java)                     # 美化检视 Java 对象/节点
mph.config 模块：option() / location() / load(file) / save(file)
```

### start() 关键参数（session.py）
- `cores`: 限制处理器核心数（默认全部）
- `version`: 选择特定 COMSOL 版本（需安装可被发现）
- 配置 `mph.option('session', ...)`：`'client-server'`（默认）| `'stand-alone'` | `'platform-dependent'`
- 配置 `mph.option('classkit', True)`：Class Kit 许可证需加 `-ckl` 参数

## Client（client.py）

| 方法 | 说明 |
|---|---|
| `load(file)` | 加载 `.mph` 文件 → `Model` |
| `create(name=None)` | 创建空模型 → `Model` |
| `names()` / `models()` / `files()` | 已管理模型的 名称 / Model 对象 / 文件路径 列表 |
| `modules()` | 当前可用的 COMSOL 模块列表 |
| `cores` | 客户端可用核心数 |
| `remove(model)` | 从内存移除指定模型 |
| `clear()` | 移除全部模型 |
| `connect(port, host='localhost')` | 作为瘦客户端连接远程 COMSOL 服务器 |
| `disconnect()` | 断开连接 |
| `caching(state=None)` | 模型树缓存开关（读/写） |
| `client / name` 运算符 | `client/'model名'` 直达模型 |
| `client.java` | COMSOL `ModelUtil` 的 Java 对象 |

## Model（model.py）

**检视类**（都返回名称字符串列表或字典）：
`functions()` `components()` `geometries()` `selections()` `physics()` `multiphysics()` `materials()` `meshes()` `studies()` `solutions()` `datasets()` `plots()` `exports()` `modules()` `problems()`
`name()` `file()` `version()`（方法，返回模型名/文件路径/COMSOL 版本）

**参数**：
```python
model.parameters(evaluate=False)      # {'U': '1[V]', ...}；evaluate=True 时数值化
model.parameter('d')                  # 读：'2[mm]'
model.parameter('d', '1[mm]')         # 写：带单位字符串
model.description('d')                # 读参数描述
model.description('d', '新描述')       # 写参数描述
model.descriptions()                  # 全部描述字典
```

**几何/网格/求解**：
```python
model.build(geometry=None)            # 重建几何（默认全部）
model.mesh(mesh=None)                 # 生成网格
model.solve(study=None)               # 求解；study 省略 = 全部研究
```

**结果**：
```python
model.inner(study)                    # (时间索引 ndarray, 时间值 ndarray)
model.outer(study)                    # (参数索引 ndarray, 参数值 ndarray)
model.evaluate(expr, unit=None, dataset=None, time=None, index=None)
```
- `expr`: 表达式字符串 或 表达式列表（返回对应个数的数组）
- `unit`: 单位字符串（如 `'pF'`）；省略 = 模型默认单位
- `dataset`: 数据集名称（省略 = 默认数据集）
- `time`: `'first'` / `'last'` 或具体时间值（瞬态研究）
- `index`: 外层参数索引（参数扫描研究）
- 返回值一律是 **NumPy 数组**（全局量可转 float）

**导出/保存**：
```python
model.export(node=None, file=None)    # 触发导出节点；file 覆盖文件名/路径
model.save(path=None, format=None)    # 保存（自动补 .mph）；path 省略 = 覆盖原文件
model.clear()                         # 清空解与网格数据（瘦身）
model.reset()                         # 重置建模历史记录
```

**模型树操作**：
```python
model.create(node, *args)             # 在 node 下创建特征（自动生成名称）
model.remove(node)                    # 删除节点
model.rename(name)                    # 重命名
model.property(node, name, value=None)  # 读写节点属性（如 'size', ('0.1','0.2','0.5')）
model.properties(node)                # 读全部属性
model.import_(node, file)             # 向节点导入文件
model / '路径/节点'                    # pathlib 风格导航
model.java                            # 该模型的 COMSOL Java 对象
```

## Node（node.py）

- `model/'geometries'/'geometry 1'` — `/` 运算符逐级导航；`model/''` 或 `model/None` = 根节点；名称含 `/` 用 `//` 转义
- `node.name` `node.tag` `node.type` `node.parent` `node.children` — 元信息
- `node.exists()` `node.is_root()` `node.is_group()`
- `node.create(type, name=None, ...)` — 创建子特征
- `node.property(name, value=None)` — 读写属性；`node.properties()`
- `node.problems()` — 模型一致性检查问题列表
- `node.select(...)` `node.selection()` `node.toggle(...)` `node.run()` `node.import_(file)` `node.remove()`
- `node.rename(name)` `node.retag(tag)` `node.comment(text=None)`
- `node.java` / `node.java_if_exists()` — 对应 Java 对象

## 辅助（node.py 模块级）

- `tree(node, max_depth=None)` — 打印模型树
- `inspect(java)` — 美化打印 Java 对象结构
- `parse(string)` / `join(path)` / `escape(name)` / `unescape(name)` — 路径工具

## Server（server.py）

- `server.running` — 服务器是否运行
- `server.stop(timeout=20)` — 停止服务器
- 由 `mph.start()` 内部创建，一般无需直接操作
