from sklearn import linear_model
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
# linear classification
# winBoundary is the value separating wins and draws
# lossBoundary is the value separating losses and draws
# final prediction

# Not sure if this is an actual algorithm lol. But sounds like a good idea to me.
def linearClassification(trainX, trainY, testX, testY, winBoundary, lossBoundary):
    # linear classification
    reg = linear_model.LinearRegression()

    # fitting the data
    reg.fit(trainX, trainY)

    # prediction
    prediction = reg.predict(testX)
    # final prediction
    finalLinear = [1.0 * (x >= winBoundary) + 0 * (x < winBoundary and x >= lossBoundary) + (-1) * (x < lossBoundary) for x in prediction]
    error = sum([1.0 * (finalLinear[i] != testY[i]) for i in range(len(finalLinear))]) / len(finalLinear)
    print "Linear classification with boundaries", lossBoundary, winBoundary, "is equal to:", error

def SVC(trainX, trainY, testX, testY):
    #print testY
    trainY1 = [1 * (x > 0) for x in trainY]
    clfWin = svm.SVC()
    clfWin.fit(trainX, trainY1)
    predictionWin = clfWin.predict(testX)
    #print predictionWin
    newTrainX = []
    newTrainY = []
    for i in range(len(trainX)):
        if trainY[i] <= 0:
            newTrainX.append(trainX[i])
            newTrainY.append(-trainY[i])
    clfLoss = svm.SVC()
    clfLoss.fit(newTrainX, newTrainY)
    predictionLoss = clfLoss.predict(testX)
    #print predictionLoss
    prediction = []
    for i in range(len(testX)):
        if predictionWin[i] == 1:
            prediction.append(1)
        else:
            if predictionLoss[i] == 1:
                prediction.append(-1)
            else:
                prediction.append(0)
                
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    print "SVC error: ", error

def NB(trainX, trainY, testX, testY, smoothing = 1):
    clf = MultinomialNB(alpha = smoothing)
    clf.fit(trainX, trainY)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    print "Naive Bayes error with smoothing =", smoothing, "is equal to:", error
