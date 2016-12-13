from sklearn import linear_model
import util
import attributeVectorIterator as a

trainYears = [ '2011/2012', '2012/2013', '2013/2014']
testYears = ['2014/2015']
dataExists = False
'''
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
'''
[trainX, trainY, order] = util.createTrainData(trainYears)
[testX, testY] = util.createTestData(testYears, order)
#[trainX, trainY] = util.fetchData("train")
#[testX, testY] = util.fetchData("test")
winBoundary = 0.5
lossBoundary = -0.5
print "FINISHED EXTRACTING TRAINING DATA"
#util.linearClassification(trainX, trainY, testX, testY, winBoundary, lossBoundary)
#util.SVC(trainX, trainY, testX, testY)
#util.layeredSVM(trainX, trainY, testX, testY)
#util.linearSVC(trainX, trainY, testX, testY)
#util.NB(trainX, trainY, testX, testY)
'''
iteration = 0
for (av, result) in a.attributeVectorIterator(trainYears):
    print av, result
    iteration += 1
    if iteration == 1:
        break
'''


kValidationRatio = 0.3
def forwardSelection(origTrainX, origTrainY, testX, testY, order, trainingAlgorithm, numIter = 0, startingFeatures = [], featuresLeft = None):
    """
    Performs forward selection 

    :param origTrainX: original training set x values
    :param origTrainY: original training set y values
    :param testX: test set x values
    :param textY: test set y values
    :param order: mapping from attributes to indexes into the feature vectors
    :param trainingAlgorithm: the training algorithm we're using, takes training and test sets, returns test error
    """
    (trainX, trainY, valX, valY) = splitData(origTrainX, origTrainY, kValidationRatio)
    featuresSelected = startingFeatures
    validationErrors = []
    if featuresLeft == None:
        remainingFeatures = order.keys()
    else: 
        remainingFeatures = featuresLeft
    if numIter == 0: numIter = len(trainX[0])
    for i in range(numIter):
        bestFeature = None
        bestFeatureError = float('inf')
        for feature in remainingFeatures:
            features = featuresSelected + [feature]
            selTrainX = selectFeatures(trainX, features, order) # selTrainX for selectedFeatures of trainX
            selValX = selectFeatures(valX, features, order)
            error = trainingAlgorithm(selTrainX, trainY, selValX, valY) # try this subset of features, and how well it does on validation set
            if error < bestFeatureError:
                bestFeature = feature
                bestFeatureError = error
                validationErrors.append(error)
        featuresSelected = featuresSelected + [bestFeature]
        remainingFeatures.remove(bestFeature)
        print ' '
        print str(i) + "th feature selected: " + bestFeature
        print features
        print "----> error:" + str(bestFeatureError)
        print ' '

    # the ith subset selected by forward selection is featuresSelected[:i] (i running from 1 to numFeratures)
    # now we try each of the subsets on the algorithm, training with the whole (original) training set, and test on final test set
    testErrors = []
    for i in range(totalNumFeatures):
        features = featuresSelected[:i+1]
        selTrainX = selectFeatures(origTrainX, features, order)
        selTestX = selectFeatures(testX, features, order)
        error = trainingAlgorithm(selTrainX, origTrainY, selTestX, testY)
        testErrors.append(error)

    # Return the order of features selected and the errors of the respective subsets
    return (featuresSelected, testErrors)

def splitData(xs, ys, ratio):
    """
    Split input feature vectors and targets into a training set and validation set
    with a ratio of (1-ratio):ratio of training:validation

    :param xs: The feature vectors
    :param ys: The targets
    :param ratio: The ratio to split the set up by
    """
    trainLen = int(len(xs) * (1 - ratio))
    return (xs[:trainLen], ys[:trainLen], xs[trainLen:], ys[trainLen:])

def selectFeatures(xs, features, order):
    """
    Takes a set of feature fectors 'xs', and reduces their dimensionality to only 
    include the subset of features, 'features'.

    :param xs: A set of feature vectors
    :param features: A subset of attributes to select in the feature vectors
    :param order: A mapping from attributes to indexes in the feature vectors
    """
    newXs = []
    for x in xs:
        newX = []
        for feature in features:
            newX.append(x[order[feature]])
        newXs.append(newX)
    return newXs



(forwardSelectedFeatures, valErrors, testErrors) = forwardSelection(trainX, trainY, testX, testY, order, util.logisticRegression, 100)
print "\n"
print "\n"
print forwardSelectedFeatures
print "\n"
print "\n"
print valErrors
print "\n"
print "\n"
print testErrors
print "\n"
print "\n"
