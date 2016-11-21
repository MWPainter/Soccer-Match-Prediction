from sklearn import linear_model
import util
import attributeVectorIterator as a

trainYears = [ '2011/2012', '2012/2013', '2013/2014']
testYears = []
dataExists = False
if not dataExists:
    util.createData(trainYears, writeToFile = True, FileName = 'Train')
    #util.createData(testYears, writeToFile = True, FileName = 'Test')

[X, Y] = util.fetchData(FileName = 'Train')
#[testX, testY] = util.fetchData(FileName = 'Test')
testX = []
testY = []
trainX = []
trainY = []
for i in range(380):
    testX.append(X[i + 760])
    testY.append(Y[i + 760])
for i in range(760):
    trainX.append(X[i])
    trainY.append(Y[i])
#print "testY:", testY
winBoundary = 0.5
lossBoundary = -0.5
util.linearClassification(trainX, trainY, testX, testY, winBoundary, lossBoundary)
util.SVC(trainX, trainY, testX, testY)
util.layeredSVM(trainX, trainY, testX, testY)
util.linearSVC(trainX, trainY, testX, testY)
#util.NB(trainX, trainY, testX, testY)
'''
iteration = 0
for (av, result) in a.attributeVectorIterator(trainYears):
    print av, result
    iteration += 1
    if iteration == 1:
        break
'''
