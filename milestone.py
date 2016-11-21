from sklearn import linear_model
import util

trainX = [[0, 0], [1,1], [2,3], [4,2], [5,3], [0,1]]
trainY = [0, 0, 1, -1, -1, 1]
testX = [[3, 3], [-1,-1], [-0.5, 0.5], [4, -1]]
testY = [0, 0, 1, -1]
winBoundary = 0.5
lossBoundary = -0.5

util.linearClassification(trainX, trainY, testX, testY, winBoundary, lossBoundary)
util.SVC(trainX, trainY, testX, testY)
util.NB(trainX, trainY, testX, testY)
