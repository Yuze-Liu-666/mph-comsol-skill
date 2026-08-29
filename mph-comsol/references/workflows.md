# MPh 典型工作流

> 代码均来自官方 docs/tutorial.md 与 docs/demonstrations.md，已按 v1.3.x API 核对。
> 演示模型 `capacitor.mph` 在仓库 `demos/` 目录：https://github.com/MPh-py/MPh/tree/main/demos

## 1. 基础工作流（官方教程流程）

```python
import mph

client = mph.start()                    # 启动 COMSOL（约 10 秒）
model = client.load('capacitor.mph')    # 加载模型

# 检视
model.parameters()      # {'U': '1[V]', 'd': '2[mm]', 'l': '10[mm]', 'w': '2[mm]'}
model.materials()       # ['medium 1', 'medium 2']
model.physics()         # ['electrostatic', 'electric currents']
model.studies()         # ['static', 'relaxation', 'sweep']

# 修改参数
model.parameter('d', '1[mm]')

# 求解（build/mesh 会自动发生，显式调用更稳）
model.build()
model.mesh()
model.solve('static')                   # 只解 'static'；model.solve() = 全部

# 评估
C = model.evaluate('2*es.intWe/U^2', 'pF')        # array(1.31948342)
(x, y, E) = model.evaluate(['x', 'y', 'es.normE'])  # 局部量，模型默认单位
E.max()                                          # 场强最大值

# 瞬态研究的时间步
model.evaluate(C, 'pF', 'time-dependent', 'first')
model.evaluate(C, 'pF', 'time-dependent', 'last')
(indices, values) = model.inner('time-dependent')  # 时间索引与值

# 参数扫描研究的参数索引
model.evaluate(C, 'pF', 'parametric sweep', 'first', 1)  # 第 1 组参数
(indices, values) = model.outer('parametric sweep')

# 导出与保存
model.export('image', 'static field.png')
model.export()                          # 触发全部导出节点
model.save('capacitor_solved')          # 自动补 .mph
```

## 2. 顺序参数扫描（Python 完全掌控）

```python
import mph
client = mph.start()
model = client.load('capacitor.mph')

for d in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    model.parameter('d', f'{d} [mm]')
    model.solve('static')
    C = model.evaluate('2*es.intWe/U^2', 'pF')
    print(d, float(C))
```

适合迭代优化（遗传算法/差分进化）：参数值来自上一代结果，无需硬编码。

## 3. 多进程并行参数扫描（multiprocessing）

> 一个 Python 进程只能有一个 COMSOL 客户端，并行必须多进程。每进程 `mph.start(cores=1)`。

```python
import mph
import multiprocessing
import queue

def worker(jobs, results):
    client = mph.start(cores=1)
    model = client.load('capacitor.mph')
    while True:
        try:
            d = jobs.get(block=False)
        except queue.Empty:
            break
        model.parameter('d', f'{d} [mm]')
        model.solve('static')
        C = model.evaluate('2*es.intWe/U^2', 'pF')
        results.put((d, C))

values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
jobs = multiprocessing.Queue()
for d in values:
    jobs.put(d)
results = multiprocessing.Queue()

processes = []
for _ in range(4):                      # 4 个 worker，各占 1 核
    p = multiprocessing.Process(target=worker, args=(jobs, results))
    p.start()
    processes.append(p)                 # 防止被 GC 回收

for _ in values:                        # 结果顺序与输入无关！
    d, C = results.get()
    print(d, C)
```

官方完整版：仓库 `demos/worker_pool.py`（带实时绘图）。进阶：任务/结果落盘以便中断续跑。

## 4. 直接调用完整 COMSOL Java API

官方 Java 示例几乎可以原样粘贴（`new String[]{"a","b"}` → `["a","b"]`）：

```python
import mph
client = mph.start()
pymodel = client.create('Model')
model = pymodel.java                    # 底层 COMSOL Java Model 对象

model.modelNode().create("comp1");
model.geom().create("geom1", 3);
model.geom("geom1").feature().create("blk1", "Block");
model.geom("geom1").feature("blk1").set("size", ["0.1", "0.2", "0.5"]);
model.geom("geom1").run("fin");
pymodel.save('model')                   # 保存回 Python 封装
```

优势：不用装 Java、不用 comsolcompile 编译；`mph.inspect(obj)` 辅助理解对象结构。

## 5. 纯 Python 方式创建模型（Node API）

```python
import mph
client = mph.start()
model = client.create('block of ice')
model.create('geometries/geometry', 3)              # 不存在则自动创建
model.create('geometries/geometry/ice block', 'Block')
model.property('geometries/geometry/ice block', 'size', ('0.1', '0.2', '0.5'))
model.build('geometry')
mph.tree(model)                                     # 打印模型树

# 或 pathlib 风格：
geometries = model/'geometries'
geometry = geometries.create(3, name='geometry')
block = geometry.create('Block', name='ice block')
block.property('size', ('0.1', '0.2', '0.5'))
model.build(geometry)
```

## 6. 模型批量瘦身（归档前压缩）

```python
import mph
from pathlib import Path

client = mph.start()
for file in Path.cwd().glob('*.mph'):
    model = client.load(file)
    model.clear()          # 清解+网格数据
    model.reset()          # 清建模历史
    model.save()
```

递归处理改用 `rglob('*.mph')`（慎用）。官方版：`demos/compact_models.py`。

## 7. Busbar 例子（GUI 教程结果复现）

```python
import mph
client = mph.start()
model = client.load('busbar.mph')
model.solve()
(x, y, z, T) = model.evaluate(['x', 'y', 'z', 'T'])
print(f'Tmax = {T.max():.2f} K at ({x[T.argmax()]}, {y[T.argmax()]}, {z[T.argmax()]})')
```

## 8. 远程服务器模式

```python
import mph
client = mph.start()          # 或由服务器端提供端口
# 另一台机器上：client = mph.Client(); client.connect(port, host='服务器地址')
```
