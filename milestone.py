from sklearn import linear_model
import util
import attributeVectorIterator as a
import random

#trainYears = [ '2011/2012', '2012/2013', '2013/2014']
#trainYears = ['2008/2009', '2009/2010', '2010/2011', '2011/2012', '2012/2013', '2013/2014']
#testYears = ['2014/2015', '2015/2016']
#testYears = ['2014/2015']
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
#[trainX, trainY, order] = util.createTrainData(trainYears, True)
#[testX, testY] = util.createTestData(testYears, order, True)
#[trainX, trainY] = util.fetchData("train")
#[testX, testY] = util.fetchData("test")
#order = util.fetchFeatureOrder("order")
winBoundary = 0.5
lossBoundary = -0.5
#print "FINISHED EXTRACTING TRAINING DATA"
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
def forwardSelection(origTrainX, origTrainY, testX, testY, order, trainingAlgorithm, numIter = -1, loggingFile = None, startingFeatures = [], featuresLeft = None):
    """
    Performs forward selection 

    :param origTrainX: original training set x values
    :param origTrainY: original training set y values
    :param testX: test set x values
    :param textY: test set y values
    :param order: mapping from attributes to indexes into the feature vectors
    :param trainingAlgorithm: the training algorithm we're using, takes training and test sets, returns test error
    :param numIter:
    :param startingFeatures:
    :param featuresLeft:
    """
    # Setup
    (trainX, trainY, valX, valY) = splitData(origTrainX, origTrainY, kValidationRatio)
    featuresSelected = startingFeatures
    validationErrors = []
    if featuresLeft == None:
        remainingFeatures = order.keys()
    else: 
        remainingFeatures = featuresLeft
    if numIter == -1: numIter = len(trainX[0])

    # Get data we've from the starting features
    for i in range(1, len(featuresSelected)):
        features = featuresSelected[:i]
        _, valerror = getErrorsForFeatureSelection(trainX, trainY, valX, valY, features, order, trainingAlgorithm)
        validationErrors.append(valerror)

    # Forward selection, main loop
    for i in range(1, numIter+1):
        bestFeature = None
        bestFeatureValError = float('inf')
        for feature in remainingFeatures:
            features = featuresSelected + [feature]
            _, valerror = getErrorsForFeatureSelection(trainX, trainY, valX, valY, features, order, trainingAlgorithm)
            if valerror < bestFeatureValError:
                bestFeature = feature
                bestFeatureValError = valerror
        validationErrors.append(bestFeatureValError)
        featuresSelected = featuresSelected + [bestFeature]
        remainingFeatures.remove(bestFeature)
        if loggingFile:
            loggingFile.write(bestFeature + " " + str(bestFeatureValError) + "\n")
        print ' '
        print str(i) + "th feature selected: " + bestFeature
        print featuresSelected
        print "----> error:" + str(bestFeatureValError)
        print ' '

    # the ith subset selected by forward selection is featuresSelected[:i] (i running from 1 to numFeratures)
    # now we try each of the subsets on the algorithm, training with the whole (original) training set, and test on final test set
    trainingErrors = []
    testErrors = []
    totalNumFeatures = len(featuresSelected)
    for i in range(totalNumFeatures):
        features = featuresSelected[:i+1]
        trainingError, testError = getErrorsForFeatureSelection(origTrainX, origTrainY, testX, testY, features, order, trainingAlgorithm)
        trainingErrors.append(trainingError)
        testErrors.append(testError)

    # Return the order of features selected and the errors of the respective subsets
    return (featuresSelected, trainingErrors, validationErrors, testErrors)

def getErrorsForFeatureSelection(trainX, trainY, testX, testY, features, order, trainingAlgorithm):
    """
    Takes training and training and test data, reduces them to use a subset of features, and returns the
    training error and test error from the training algoritm
    
    N.B. Often we have that training set passed in is a validation set
    """
    selTrainX = selectFeatures(trainX, features, order) # selTrainX for selectedFeatures of trainX
    selTestX = selectFeatures(testX, features, order)
    return trainingAlgorithm(selTrainX, trainY, selTestX, testY) # try this subset of features, and how well it does on validation set


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


#features = ['awayLeaguePosition', 'home_player_8_-positioning', 'away_player_10_-dribbling', 'home_player_6_-curve', 'home_player_2_-heading_accuracy', u'away_team_-defenceAggressionClass-Press', u'awayTeamName-Southampton', u'home_player_5_-attacking_work_rate-low', 'homeFormation-3-5-1-1', 'awayFormation-5-1-1-2-1', u'away_player_9_-attacking_work_rate-low', 'home_player_8_-strength', 'home_player_10_height', 'away_player_11_-marking', u'away_player_2_-defensive_work_rate-7', u'awayTeamName-Wolverhampton Wanderers', u'home_team_-buildUpPlayPassingClass-Short', 'away_player_3_-sprint_speed', 'awayFormation-4-1-4-1', u'home_team_-defenceAggressionClass-Contain', 'home_player_6_-sprint_speed', 'away_player_9_-gk_kicking', 'homeFormation-3-5-2', u'away_player_4_-defensive_work_rate-1', u'away_player_1_-defensive_work_rate-0', 'homeFormation-4-1-3-1-1', 'home_player_7_height', 'homeFormation-3-4-3', 'homeFormation-4-2-1-1-1-1', 'awayFormation-3-5-1-1', 'home_player_2_-crossing', u'awayTeamName-Norwich City', 'awayFormation-4-1-1-1-2-1', 'homeFormation-4-3-1-1-1', 'homeFormation-4-2-2-2', u'home_player_4_-defensive_work_rate-low', 'home_player_10_-standing_tackle', 'homeFormation-4-1-2-1-2', u'away_player_7_-defensive_work_rate-low', 'awayFormation-5-4-1', u'away_team_-chanceCreationCrossingClass-Little', 'awayFormation-4-2-2-2', 'awayFormation-4-1-2-1-1-1', 'homeFormation-4-1-1-2-1-1', u'home_team_-chanceCreationCrossingClass-Little', u'away_player_5_-defensive_work_rate-medium']
#features = ['away_player_9_-short_passing', 'homeTeamName-Everton', 'homeTeamName-Chelsea', 'home_player_4_-defensive_work_rate-medium', 'away_player_7_-defensive_work_rate-high', 'home_player_7_-defensive_work_rate-medium', 'away_player_10_-defensive_work_rate-high', 'homeTeamName-Manchester City', 'home_team_-chanceCreationCrossingClass-Normal', 'homeTeamName-Arsenal', 'away_team_-chanceCreationCrossingClass-Normal', 'awayFormation-4-4-2', 'away_player_5_-attacking_work_rate-low', 'home_player_1_-attacking_work_rate-medium', 'away_player_5_-defensive_work_rate-high', 'awayTeamName-Aston Villa', 'home_team_-chanceCreationCrossingClass-Lots', 'home_player_5_-attacking_work_rate-low', 'away_player_6_-defensive_work_rate-low', 'away_player_6_-defensive_work_rate-high', 'away_team_-defenceAggressionClass-Press', 'awayTeamName-Newcastle United', 'awayFormation-4-1-4-1', 'home_team_-chanceCreationShootingClass-Little', 'homeFormation-3-4-3', 'away_player_2_-attacking_work_rate-low', 'home_player_10_-attacking_work_rate-medium', 'home_player_6_-attacking_work_rate-high', 'home_player_8_-attacking_work_rate-low', 'home_team_-buildUpPlayPassingClass-Short', 'awayTeamName-Everton', 'away_player_10_-attacking_work_rate-low', 'awayTeamName-Wolverhampton Wanderers', 'away_player_7_-defensive_work_rate-low', 'homeTeamName-Norwich City', 'away_player_3_-attacking_work_rate-medium', 'away_player_2_-defensive_work_rate-7', 'away_player_9_-defensive_work_rate-low', 'away_player_10_-attacking_work_rate-high']

def shuffleData(trainX, trainY, testX, testY):
    allData = [(trainX[i],trainY[i]) for i in range(len(trainX))]
    allData = allData + [(testX[i],testY[i]) for i in range(len(testX))]
    random.shuffle(allData)
    xs = [x for (x,_) in allData]
    ys = [y for (_,y) in allData]
    return splitData(xs, ys, 0.25)


#[trainX, trainY, order] = util.createTrainData(trainYears, True)
#[testX, testY] = util.createTestData(testYears, order, True)
[trainX, trainY] = util.fetchData("trainNoPlayer")
[testX, testY] = util.fetchData("testNoPlayer")
order = util.fetchFeatureOrder("orderNoPlayer")
(trainX, trainY, testX, testY) = shuffleData(trainX, trainY, testX, testY)


algorithms = [util.SVC, util.linearSVC, util.logisticRegression] #, util.layeredSVM, util.linearClassification, util.NB] # need to add the neural network in
algorithmNames = ['SVC', 'linearSVC', 'softmaxRegression'] #, 'layeredSVM', 'linearClassification', 'NB']

fo = open('forwardSearchResults', 'a', 0)

# first thing, full forward selection on one to estimate optimal size
def fullFeatureSelectSVC():
    fo.write("~~~ START: full forward selection on SVC ~~~\n")
    (selFeats, trainErrs, valErrs, testErrs) = forwardSelection(trainX, trainY, testX, testY, order, util.SVC, -1, fo)
    
    fo.write("\n\n\n")
    fo.write("~~~ RESULTS: full forward selection on SVC ~~~\n")
    fo.write("features: "+str(selFeats)+"\n")
    fo.write("trainerrs:"+str(trainErrs)+"\n")
    fo.write("valerrs"+str(valErrs)+"\n")
    fo.write("testerrs:"+str(testErrs)+"\n")
    fo.write("\n\n\n")


# Select num features bases on above, with only team attributes
numFeatures = 30
def noPlayerFeatureSelect():
    for algorithm in algorithms:
        algName = algorithmNames[algorithms.index(algorithm)]
        fo.write("~~~ START forward selection on " + algName + " ~~~\n")
        (selFeats, trainErrs, valErrs, testErrs) = forwardSelection(trainX, trainY, testX, testY, order, algorithm, numFeatures, fo)

        fo.write("\n\n\n")
        fo.write("~~~ RESULTS forward selection on " + algName + " ~~~\n")
        fo.write("features: "+str(selFeats)+"\n")
        fo.write("trainerrs:"+str(trainErrs)+"\n")
        fo.write("valerrs"+str(valErrs)+"\n")
        fo.write("testerrs:"+str(testErrs)+"\n")
        fo.write("\n\n\n")


# Same again with the number of features, including team attributes
def playerFeatureSelect():
    [trainX, trainY] = util.fetchData("fulltrain")
    [testX, testY] = util.fetchData("fulltest")
    order = util.fetchFeatureOrder("fullorder")
    (trainX, trainY, testX, testY) = shuffleData(trainX, trainY, testX, testY)
    for algorithm in algorithms:
        algName = algorithmNames[algorithms.index(algorithm)]
        fo.write("~~~ START: forward selection (with player features) on " + algName + " ~~~\n")
        (selFeats, trainErrs, valErrs, testErrs) = forwardSelection(trainX, trainY, testX, testY, order, algorithm, numFeatures, fo)

        fo.write("\n\n\n")
        fo.write("~~~ RESULTS: forward selection (with player features) on " + algName + " ~~~\n")
        fo.write("features: "+str(selFeats)+"\n")
        fo.write("trainerrs:"+str(trainErrs)+"\n")
        fo.write("valerrs"+str(valErrs)+"\n")
        fo.write("testerrs:"+str(testErrs)+"\n")
        fo.write("\n\n\n")


# now pick the best set of features coupled with the best set of algorithms
# look at regularisation penalty
def pickRegularisation():
    bestAlgorithm = util.logisticRegression
    fo.write("~~~ START: regularization parameter training ~~~\n")
    features = ['awayLeaguePosition', 'homeGameHistoryScore', 'homeFormation-4-2-3-1', 'away_team_-chanceCreationPassingClass-Normal', 
		'homeFormation-4-1-4-1', 'homeFormation-4-3-2-1', 'home_team_-chanceCreationPassingClass-Safe', 'homeTeamName-Manchester United', 
		'awayFormation-4-3-1-2', 'awayFormation-4-1-3-2', 'home_team_-defencePressureClass-Medium', 'awayTeamName-Middlesbrough', 
		'home_team_-defenceTeamWidthClass-Wide', 'awayTeamName-Sunderland', 'awayFormation-4-4-1-1', 'awayFormation-4-1-2-3', 
		'awayTeamName-Fulham', 'awayTeamName-Cardiff City', 'homeFormation-3-4-1-2', 'awayFormation-5-3-2', 'homeFormation-4-3-1-2', 
		'awayFormation-3-4-1-2', 'awayFormation-4-1-3-1-1', 'homeFormation-5-3-1-1', 'awayTeamName-Southampton', 'awayTeamName-Birmingham City', 
		'homeFormation-5-3-2', 'homeFormation-4-2-1-1-1-1', 'awayFormation-4-2-1-3', 'awayFormation-3-5-1-1']
    trainErrs = []
    testErrs = []
    for i in range(1,101):
        trainErr, testErr = bestAlgorithm(trainX, trainY, testX, testY, i*0.0005)
        trainErrs.append(trainErr)
        testErrs.append(testErr)
        print trainErr
        print testErr

    fo.write("\n\n\n")
    fo.write("~~~ RESULTS: regularisation coefficient ~~~\n")
    fo.write("trainerrs: "+str(trainErrs)+"\n")
    fo.write("testerrs: "+str(testErrs)+"\n")
    fo.write("\n\n\n")

# todo: split test output (have full error, plus 10 arrays of errors)
# ---- do at end on one model (see what happens)
# ML filter feature selection
# todo: write stuff to work out the best regularisation penalty (and add that to all of the algorithms as input, with default of 1
# todo: write stuff to work out training set size vs errors

#def pickTrainingSetSize3Season():
    #for i in range(1140):
        # todo: shuffle training data, and take the first i items from it


#def pickTrainingSetSize6Seasion():
    #for i in range(1140, 2280):
        # todo: shuffle training data and take first i items from it
    


#fullFeatureSelectSVC()          # run full feature selection on SVC, just to confirm 70etc isn't any better
#noPlayerFeatureSelect()        # feature selection without player features
#playerFeatureSelect()          # feature selection with player features
#miFeatureSelect()              # mutual information feature selection
pickRegularisation()           # regulaisation hyperperameter training
#pickTrainingSetSize3Season()   # part 1: see how training set size effects training
#pickTrainingSetSize6Season()   # part 2: see how training set size effects training

"""
features = ['awayLeaguePosition', 'homeGameHistoryScore', 'homeFormation-4-2-3-1', 'away_team_-chanceCreationPassingClass-Normal', 'homeFormation-4-1-4-1', 'homeFormation-4-3-2-1', 'home_team_-chanceCreationPassingClass-Safe', 'homeTeamName-Manchester United', 'awayFormation-4-3-1-2', 'awayFormation-4-1-3-2', 'home_team_-defencePressureClass-Medium', 'awayTeamName-Middlesbrough', 'home_team_-defenceTeamWidthClass-Wide', 'awayTeamName-Sunderland', 'awayFormation-4-4-1-1', 'awayFormation-4-1-2-3', 'awayTeamName-Fulham', 'awayTeamName-Cardiff City', 'homeFormation-3-4-1-2', 'awayFormation-5-3-2', 'homeFormation-4-3-1-2', 'awayFormation-3-4-1-2', 'awayFormation-4-1-3-1-1', 'homeFormation-5-3-1-1', 'awayTeamName-Southampton', 'awayTeamName-Birmingham City', 'homeFormation-5-3-2', 'homeFormation-4-2-1-1-1-1', 'awayFormation-4-2-1-3', 'awayFormation-3-5-1-1', 'away_team_-buildUpPlayPassingClass-Long', 'awayTeamName-Arsenal', 'homeTeamName-Liverpool', 'homeTeamName-Newcastle United', 'homeFormation-3-4-3', 'away_team_-chanceCreationPositioningClass-Organised', 'homeFormation-4-1-2-3', 'homeFormation-4-4-1-1', 'homeFormation-4-1-2-1-1-1', 'home_team_-defenceAggressionClass-Press', 'away_team_-chanceCreationShootingClass-Little', 'homeTeamName-Norwich City', 'awayFormation-5-1-1-2-1', 'awayFormation-3-4-2-1', 'homeFormation-4-1-2-1-2', 'awayFormation-5-4-1', 'away_team_-defenceAggressionClass-Contain', 'homeTeamName-Swansea City', 'homeTeamName-Arsenal', 'awayTeamName-Liverpool']
featuresLeft = []
for feature in order:
    if not(feature in features):
        featuresLeft.append(feature)
fo.write("~~~ START forward selection on " + 'softmaxRegression' + " ~~~\n")
(selFeats, trainErrs, valErrs, testErrs) = forwardSelection(trainX, trainY, testX, testY, order, util.logisticRegression, 0, fo, features, [])
fo.write("\n\n\n")
fo.write("~~~ RESULTS: forward selection (with player features) on " + 'softmaxRegression' + " ~~~\n")
fo.write("features: "+str(selFeats)+"\n")
fo.write("trainerrs:"+str(trainErrs)+"\n")
fo.write("valerrs"+str(valErrs)+"\n")
fo.write("testerrs:"+str(testErrs)+"\n")
fo.write("\n\n\n")
"""


fo.close()
