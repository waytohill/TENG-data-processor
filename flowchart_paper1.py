from graphviz import Digraph

# 创建有向图
dot = Digraph(comment='TENG信号处理流程', format='svg', 
             graph_attr={'rankdir': 'LR', 'splines': 'ortho', 'nodesep': '0.5'},
             node_attr={'shape': 'box', 'style': 'rounded,filled', 'fillcolor': '#F0F8FF'})

# 添加节点
dot.node('A', '原始信号读取\n(CSV文件加载)', shape='ellipse', fillcolor='#FFF8DC')
dot.node('B', '预处理阶段\n(时间列检查/创建)', fillcolor='#FFEBCD')
dot.node('C1', '形态学基线去除\n(开闭运算)', fillcolor='#E6E6FA')
dot.node('C2', '陷波滤波\n(去除工频噪声)', fillcolor='#E0FFFF')
dot.node('C3', '小波去噪\n(细节降噪)', fillcolor='#F0FFF0')
dot.node('C4', 'Savitzky-Golay滤波\n(局部平滑)', fillcolor='#FFF0F5')
dot.node('C5', '移动平均平滑\n(全局平滑)', fillcolor='#F8F8FF')
dot.node('C6', '最终形态学信号', shape='ellipse', fillcolor='#FFF8DC')

dot.node('D1', '中值/平均基线去除\n(滑动窗口)', fillcolor='#E6E6FA')
dot.node('D2', 'Savitzky-Golay滤波\n(局部平滑)', fillcolor='#FFF0F5')
dot.node('D3', '移动平均平滑\n(全局平滑)', fillcolor='#F8F8FF')
dot.node('D4', '最终平均信号', shape='ellipse', fillcolor='#FFF8DC')

dot.node('E', '包络线分析\n(上下包络/差值)', fillcolor='#FFE4E1')
dot.node('F', '可视化系统\n(8子图实时展示)', fillcolor='#FFDAB9')
dot.node('G', '结果输出\n(图像/数据保存)', shape='ellipse', fillcolor='#FFF8DC')

# 添加边
dot.edge('A', 'B')
dot.edge('B', 'C1', label='形态学路径')
dot.edge('B', 'D1', label='平均路径')
dot.edges([('C1', 'C2'), ('C2', 'C3'), ('C3', 'C4'), ('C4', 'C5'), ('C5', 'C6')])
dot.edges([('D1', 'D2'), ('D2', 'D3'), ('D3', 'D4')])
dot.edge('C6', 'E')
dot.edge('D4', 'E')
dot.edge('E', 'F')
dot.edge('F', 'G')

# 添加参数节点
with dot.subgraph(name='cluster_params') as c:
    c.attr(style='dashed', label='自适应参数系统', color='gray')
    c.node('P1', '频率×采样率\n=窗口尺寸', fillcolor='#F5F5DC')
    c.node('P2', '智能边界处理', fillcolor='#F5F5DC')
    c.node('P3', '自动NaN处理', fillcolor='#F5F5DC')
    c.edges([('P1', 'P2'), ('P2', 'P3')])
    
    # 连接到处理节点
    c.edge('P1', 'C1', style='dashed', color='gray')
    c.edge('P1', 'D1', style='dashed', color='gray')
    c.edge('P2', 'C5', style='dashed', color='gray')
    c.edge('P2', 'D3', style='dashed', color='gray')
    c.edge('P3', 'C4', style='dashed', color='gray')
    c.edge('P3', 'D2', style='dashed', color='gray')

# 添加分析系统
with dot.subgraph(name='cluster_analysis') as c:
    c.attr(style='filled', label='多维分析系统', color='lightblue', fillcolor='#F0FFFF')
    c.node('A1', '时域分析', fillcolor='#E0FFFF')
    c.node('A2', '频域分析\n(FFT/STFT/CWT)', fillcolor='#E0FFFF')
    c.node('A3', '包络分析', fillcolor='#E0FFFF')
    c.edges([('A1', 'A2'), ('A2', 'A3')])
    c.edge('A1', 'F', style='dashed', color='blue')
    c.edge('A2', 'F', style='dashed', color='blue')
    c.edge('A3', 'E', style='dashed', color='blue')

# 保存并渲染
dot.render('teng_signal_processing_flowchart', view=True)

# 返回DOT源代码
print(dot.source)