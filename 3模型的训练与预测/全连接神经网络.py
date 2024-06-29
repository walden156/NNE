# 导入需要的库
'''
使用tensorflow的顺序模型实现全连接神经网络
'''
import pandas as pd
import numpy as np
from keras.models import Sequential
from tensorflow.python.keras.layers.core import Dense, Activation
import tensorflow as tf

# 混淆矩阵可视化


def cm_plot(y, yp):  # 混淆矩阵可视化

    from sklearn.metrics import confusion_matrix  # 导入混淆矩阵函数

    cm = confusion_matrix(y, yp)  # 混淆矩阵

    import matplotlib.pyplot as plt  # 导入作图库
    plt.matshow(cm)  # 画混淆矩阵图，配色风格使用cm.Greens，更多风格请参考官网。
    plt.colorbar()  # 颜色标签

    for x in range(len(cm)):  # 数据标签
        for y in range(len(cm)):
            plt.annotate(cm[x, y], xy=(x, y),
                         horizontalalignment='center', verticalalignment='center')

    plt.xlabel('True label')  # 坐标轴标签
    plt.ylabel('Predicted label')  # 坐标轴标签
    return plt


# 使用随机种子使得训练过程可复现，一般情况每次训练的精度会有略微不同，这是由于算法特性所导致
tf.random.set_seed(1)
# 导入训练集
filename = '../2数据预处理/训练集.csv'
data = pd.read_csv(filename, encoding='gbk')
# 去除空集重新排序
data = data.dropna()
data = data.sort_values('类别', ascending=False)
# 分开特征矩阵和类别矩阵
X = data.iloc[:, 1:22]
X.astype(np.float32)
y = data.iloc[:, 22].astype(int)
#  实例化模型
model = Sequential()  # 建立顺序模型
model.add(Dense(input_dim=21, units=64))  # 全连接层，21进64出
model.add(Activation('relu'))  # 使用relu激活函数
model.add(Dense(input_dim=64, units=1))  # 全连接层，64进1出
model.add(Activation('sigmoid'))  # 由于是0-1输出，用sigmoid函数作为激活函数
# 使用二分类交叉熵作为损失函数，优化器梯度下降法
model.compile(loss='binary_crossentropy', optimizer='adam')
# 开始训练
# 训练次数100次，次数过多会造成过拟合，即测试精度很高但泛化精度降低，训练批次为10每次
model.fit(X, y, epochs=100, batch_size=10)

# 测试集精度
test = pd.read_csv('../2数据预处理/测试集.csv', encoding='gbk')
test = test.dropna()
test = test.sort_values('类别', ascending=False)
X = test.iloc[:, 1:22]
y = test.iloc[:, 22]
yp = (model.predict(X, batch_size=10) > 0.5).astype("int32").reshape(len(y))
cm_plot(y, yp).show()
accuracy = float((yp == y).astype(int).sum()) / float(y.size)
print(f'测试集的精度为{accuracy}')

# 泛化性能测试实战
erkang = pd.read_csv('../2数据预处理/尔康.csv', encoding='gbk')
erkang.iloc[:, 4:25]
X = erkang.iloc[:, 4:25]
X.astype(np.float32)
y = np.array([[1], [1], [1], [1], [1], [1], [1], [1],
             [0], [0], [0], [0], [0], [0], [0], [0]])
# 按照真实情况，前8个为尔康制药（财务造假，类别为1），后8个为中国医药（未造假，类别未0）
# 进行预测
y_predict = model.predict(X)
yp = y_predict.round(0).astype(int)
print(f'模型的预测结果未：{yp}')
cm_plot(y, yp).show()

# 输出结果
ls = []
for i in yp:
    k = '违规' if i == 1 else '未违规'
    ls.append(k)
erkang['是否违规'] = ls
erkang.to_csv('是否财务造假.csv')
