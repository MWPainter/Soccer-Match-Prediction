from sklearn import linear_model
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from collections import defaultdict
import attributeVectorIterator as a

def fetchData(fileName):
    xf = open(fileName + 'X' + '.txt', 'r')
    X = []
    l = []
    for line in xf:
        x = map(float, line.split())
        l.append(len(x))
        X.append(x)
    #print FileName, 'X', l
    xf.close()
    yf = open('Y' + FileName + '.txt', 'r')
    Y = map(int, yf.readline().split())
    yf.close()
    return [X, Y]

def createTrainData(years, writeToFile = False, FileName = ''):
    X = []
    Y = []
    if writeToFile:
        xf = open('trainX' + FileName + '.txt', 'w')
        yf = open('trainY' + FileName + '.txt', 'w')

    order = defaultdict(list)
    length = 0
    
    for (av, result) in a.attributeVectorIterator(years):
        for key in av:
            if key not in order:
                order[key] = length
                length += 1
    
    for (av, result) in a.attributeVectorIterator(years):
        # preparing newX
        newX = [0] * length
        for key in av:
            newX[order[key]] = av[key]

        # preparing newY
        if result[0] == result[1]:
            newY = 0
        elif result[0] > result[1]:
            newY = 1
        else:
            newY = -1

        # saving results to file if need be
        if writeToFile:
            for i in newX:
                xf.write("%s " %i)
            yf.write("%s " %newY)
            xf.write("\n")
        X.append(newX)
        Y.append(newY)
    #print len(newX)
    if writeToFile:
        xf.close()
        yf.close()        
    return [X, Y, order]

def createTestData(years, order, writeToFile = False, FileName = ''):
    X = []
    Y = []
    if writeToFile:
        xf = open('testX' + FileName + '.txt', 'w')
        yf = open('testY' + FileName + '.txt', 'w')

    length = len(order)
    for (av, result) in a.attributeVectorIterator(years):
        # preparing newX
        newX = [0] * length
        for key in av:
            if key in order:
                newX[order[key]] = av[key]

        # preparing newY
        if result[0] == result[1]:
            newY = 0
        elif result[0] > result[1]:
            newY = 1
        else:
            newY = -1

        # saving results to file if need be
        if writeToFile:
            for i in newX:
                xf.write("%s " %i)
            yf.write("%s " %newY)
            xf.write("\n")
        X.append(newX)
        Y.append(newY)
    #print len(newX)
    if writeToFile:
        xf.close()
        yf.close()        
    return [X, Y]

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
    return error

def layeredSVM(trainX, trainY, testX, testY):
    #print testY
    trainY1 = [1 * (x > 0) for x in trainY]
    clfWin = svm.SVC()
    clfWin.fit(trainX, trainY1)
    predictionWin = clfWin.predict(testX)
    #print "Prediction win:", predictionWin
    newTrainX = []
    newTrainY = []
    for i in range(len(trainX)):
        if trainY[i] <= 0:
            newTrainX.append(trainX[i])
            newTrainY.append(-trainY[i])
    clfLoss = svm.SVC()
    clfLoss.fit(newTrainX, newTrainY)
    predictionLoss = clfLoss.predict(testX)
    #print "Prediction Loss:", predictionLoss
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
    print "Layered SVM error: ", error
    return error

def SVC(trainX, trainY, testX, testY):
    clf = svm.SVC(decision_function_shape='ovo')
    clf.fit(trainX, trainY)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    print "Multiclass SVM error (SVC):", error
    return error

def linearSVC(trainX, trainY, testX, testY):
    clf = svm.LinearSVC()
    clf.fit(trainX, trainY)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    print "linear SVC error (SVC):", error
    return error

def NB(trainX, trainY, testX, testY, smoothing = 1):
    clf = MultinomialNB(alpha = smoothing)
    clf.fit(trainX, trainY)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    print "Naive Bayes error with smoothing =", smoothing, "is equal to:", error
    return error




'''
    formationIndex = defaultdict(int)
    teamIndex = defaultdict(int)
    chanceCreationPassingClassIndex = defaultdict(int)
    defenceDefenderLineClassIndex = defaultdict(int)
    buildUpPlayDribblingClassIndex = defaultdict(int)
    defenceAggressionClassIndex = defaultdict(int)
    buildUpPlayDribblingIndex = defaultdict(int)
    chanceCreationCrossingClassIndex = defaultdict(int)
    defencePressureClassIndex = defaultdict(int)
    chanceCreationPositioningClassIndex = defaultdict(int)
    buildUpPlayPassingClassIndex = defaultdict(int)
    defenceTeamWidthClassIndex = defaultdict(int)
    buildUpPlayPositioningClassIndex = defaultdict(int)
    defenceAggressionClassIndex = defaultdict(int)
    defenceDefenderLineClassIndex = defaultdict(int)
    
    indexchanceCreationPassingClass = 0
    indexdefenceDefenderLineClass = 0
    indexbuildUpPlayDribblingClass = 0
    indexdefenceAggressionClass = 0
    indexbuildUpPlayDribbling = 0
    indexchanceCreationCrossingClass = 0
    indexdefencePressureClass = 0
    indexchanceCreationPositioningClass = 0
    indexbuildUpPlayPassingClass = 0
    indexdefenceTeamWidthClass = 0
    indexbuildUpPlayPositioningClass = 0
    indexdefenceAggressionClass = 0
    indexdefenceDefenderLineClass = 0    
    indexFormation = 0
    indexName = 0
    
    for (av, result) in a.attributeVectorIterator(years):
        if av['homeFormation'] not in formationIndex:
            formationIndex[av['homeFormation']] = indexFormation
            indexFormation += 1
        if av['awayFormation'] not in formationIndex:
            formationIndex[av['awayFormation']] = indexFormation
            indexFormation += 1

        if av['homeTeamName'] not in teamIndex:
            teamIndex[av['homeTeamName']] = indexName
            indexName += 1
        if av['awayTeamName'] not in teamIndex:
            teamIndex[av['awayTeamName']] = indexName
            indexName += 1

        if av['away_team_chanceCreationPassingClass'] not in chanceCreationPassingClassIndex:
            chanceCreationPassingClassIndex[av['away_team_chanceCreationPassingClass']] = indexchanceCreationPassingClass
            indexchanceCreationPassingClass += 1
        if av['home_team_chanceCreationPassingClass'] not in chanceCreationPassingClassIndex:
            chanceCreationPassingClassIndex[av['home_team_chanceCreationPassingClass']] = indexchanceCreationPassingClass
            indexchanceCreationPassingClass += 1

        if av['home_team_defenceDefenderLineClass'] not in defenceDefenderLineClassIndex:
            defenceDefenderLineClassIndex[av['home_team_defenceDefenderLineClass']] = indexdefenceDefenderLineClass
            indexdefenceDefenderLineClass += 1
        if av['away_team_defenceDefenderLineClass'] not in defenceDefenderLineClassIndex:
            defenceDefenderLineClassIndex[av['away_team_defenceDefenderLineClass']] = indexdefenceDefenderLineClass
            indexdefenceDefenderLineClass += 1

        if av['home_team_buildUpPlayDribblingClass'] not in buildUpPlayDribblingClassIndex:
            buildUpPlayDribblingClassIndex[av['home_team_buildUpPlayDribblingClass']] = indexbuildUpPlayDribblingClass
            indexbuildUpPlayDribblingClass += 1
        if av['away_team_buildUpPlayDribblingClass'] not in buildUpPlayDribblingClassIndex:
            buildUpPlayDribblingClassIndex[av['away_team_buildUpPlayDribblingClass']] = indexbuildUpPlayDribblingClass
            indexbuildUpPlayDribblingClass += 1

        if av['home_team_defenceAggressionClass'] not in defenceAggressionClassIndex:
            defenceAggressionClassIndex[av['home_team_defenceAggressionClass']] = indexdefenceAggressionClass
            indexdefenceAggressionClass += 1
        if av['away_team_defenceAggressionClass'] not in defenceAggressionClassIndex:
            defenceAggressionClassIndex[av['away_team_defenceAggressionClass']] = indexdefenceAggressionClass
            indexdefenceAggressionClass += 1

        if av['home_team_buildUpPlayDribbling'] not in buildUpPlayDribblingIndex:
            buildUpPlayDribblingIndex[av['home_team_buildUpPlayDribbling']] = indexbuildUpPlayDribbling
            indexbuildUpPlayDribbling += 1
        if av['away_team_buildUpPlayDribbling'] not in buildUpPlayDribblingIndex:
            buildUpPlayDribblingIndex[av['away_team_buildUpPlayDribbling']] = indexbuildUpPlayDribbling
            indexbuildUpPlayDribbling += 1

        if av['home_team_chanceCreationCrossingClass'] not in chanceCreationCrossingClassIndex:
            chanceCreationCrossingClassIndex[av['home_team_chanceCreationCrossingClass']] = indexchanceCreationCrossingClass
            indexchanceCreationCrossingClass += 1
        if av['away_team_chanceCreationCrossingClass'] not in chanceCreationCrossingClassIndex:
            chanceCreationCrossingClassIndex[av['away_team_chanceCreationCrossingClass']] = indexchanceCreationCrossingClass
            indexchanceCreationCrossingClass += 1

        if av['home_team_defencePressureClass'] not in defencePressureClassIndex:
            defencePressureClassIndex[av['home_team_defencePressureClass']] = indexdefencePressureClass
            indexdefencePressureClass += 1
        if av['away_team_defencePressureClass'] not in defencePressureClassIndex:
            defencePressureClassIndex[av['away_team_defencePressureClass']] = indexdefencePressureClass
            indexdefencePressureClass += 1

        if av['home_team_chanceCreationPositioningClass'] not in chanceCreationPositioningClassIndex:
            chanceCreationPositioningClassIndex[av['home_team_chanceCreationPositioningClass']] = indexchanceCreationPositioningClass
            indexchanceCreationPositioningClass += 1
        if av['away_team_chanceCreationPositioningClass'] not in chanceCreationPositioningClassIndex:
            chanceCreationPositioningClassIndex[av['away_team_chanceCreationPositioningClass']] = indexchanceCreationPositioningClass
            indexchanceCreationPositioningClass += 1        

        if av['home_team_buildUpPlayPassingClass'] not in buildUpPlayPassingClassIndex:
            buildUpPlayPassingClassIndex[av['home_team_buildUpPlayPassingClass']] = indexbuildUpPlayPassingClass
            indexbuildUpPlayPassingClass += 1
        if av['away_team_buildUpPlayPassingClass'] not in buildUpPlayPassingClassIndex:
            buildUpPlayPassingClassIndex[av['away_team_buildUpPlayPassingClass']] = indexbuildUpPlayPassingClass
            indexbuildUpPlayPassingClass += 1 

        if av['home_team_defenceTeamWidthClass'] not in defenceTeamWidthClassIndex:
            defenceTeamWidthClassIndex[av['home_team_defenceTeamWidthClass']] = indexdefenceTeamWidthClass
            indexdefenceTeamWidthClass += 1
        if av['away_team_defenceTeamWidthClass'] not in defenceTeamWidthClassIndex:
            defenceTeamWidthClassIndex[av['away_team_defenceTeamWidthClass']] = indexdefenceTeamWidthClass
            indexdefenceTeamWidthClass += 1

        if av['home_team_buildUpPlayPositioningClass'] not in buildUpPlayPositioningClassIndex:
            buildUpPlayPositioningClassIndex[av['home_team_buildUpPlayPositioningClass']] = indexbuildUpPlayPositioningClass
            indexbuildUpPlayPositioningClass += 1
        if av['away_team_buildUpPlayPositioningClass'] not in buildUpPlayPositioningClassIndex:
            buildUpPlayPositioningClassIndex[av['away_team_buildUpPlayPositioningClass']] = indexbuildUpPlayPositioningClass
            indexbuildUpPlayPositioningClass += 1

        if av['home_team_defenceAggressionClass'] not in defenceAggressionClassIndex:
            defenceAggressionClassIndex[av['home_team_defenceAggressionClass']] = indexdefenceAggressionClass
            indexdefenceAggressionClass += 1
        if av['away_team_defenceAggressionClass'] not in defenceAggressionClassIndex:
            defenceAggressionClassIndex[av['away_team_defenceAggressionClass']] = indexdefenceAggressionClass
            indexdefenceAggressionClass += 1

        if av['home_team_defenceDefenderLineClass'] not in defenceDefenderLineClassIndex:
            defenceDefenderLineClassIndex[av['home_team_defenceDefenderLineClass']] = indexdefenceDefenderLineClass
            indexdefenceDefenderLineClass += 1
        if av['away_team_defenceDefenderLineClass'] not in defenceDefenderLineClassIndex:
            defenceDefenderLineClassIndex[av['away_team_defenceDefenderLineClass']] = indexdefenceDefenderLineClass
            indexdefenceDefenderLineClass += 1
'''
'''
    print indexchanceCreationPassingClass
    print indexdefenceDefenderLineClass 
    print indexbuildUpPlayDribblingClass 
    print indexdefenceAggressionClass 
    print indexbuildUpPlayDribbling 
    print indexchanceCreationCrossingClass 
    print indexdefencePressureClass 
    print indexchanceCreationPositioningClass 
    print indexbuildUpPlayPassingClass 
    print indexdefenceTeamWidthClass 
    print indexbuildUpPlayPositioningClass 
    print indexdefenceAggressionClass
    print indexdefenceDefenderLineClass
    print indexFormation 
    print 'here', indexName
'''
'''
    for (av, result) in a.attributeVectorIterator(years):
        newX = []
        newX.append(av['homeGameHistoryScore'])
        newX.append(av['awayGameHistoryScore'])
        newX.append(av['homeTimeSinceLastMatch'])
        newX.append(av['awayTimeSinceLastMatch'])
        newX.append(av['homeLeaguePosition'])
        newX.append(av['awayLeaguePosition'])
        newX.append(av['home_team_defencePressure'])
        newX.append(av['away_team_defencePressure'])
        newX.append(av['home_team_buildUpPlaySpeed'])
        newX.append(av['away_team_buildUpPlaySpeed'])
        newX.append(av['home_team_chanceCreationPassing'])
        newX.append(av['away_team_chanceCreationPassing'])
        newX.append(av['home_team_chanceCreationCrossing'])
        newX.append(av['away_team_chanceCreationCrossing'])
        newX.append(av['home_team_buildUpPlayPassing'])
        newX.append(av['away_team_buildUpPlayPassing'])
        newX.append(av['home_team_defenceTeamWidth'])
        newX.append(av['away_team_defenceTeamWidth'])
        newX.append(av['home_team_defenceAggression'])
        newX.append(av['away_team_defenceAggression'])
        for i in range(len(formationIndex)):
            newX.append(1 * (i == formationIndex[av['homeFormation']]))
            newX.append(1 * (i == formationIndex[av['awayFormation']]))
        for i in range(len(teamIndex)):
            newX.append(1 * (i == teamIndex[av['homeTeamName']]))
            newX.append(1 * (i == teamIndex[av['awayTeamName']]))
        for i in range(len(chanceCreationPassingClassIndex)):
            newX.append(1 * (i == chanceCreationPassingClassIndex[av['home_team_chanceCreationPassingClass']]) * (chanceCreationPassingClassIndex[av['home_team_chanceCreationPassingClass']] != None))
            newX.append(1 * (i == chanceCreationPassingClassIndex[av['away_team_chanceCreationPassingClass']]) * (chanceCreationPassingClassIndex[av['away_team_chanceCreationPassingClass']] != None))
        for i in range(len(defenceDefenderLineClassIndex)):
            newX.append(1 * (i == defenceDefenderLineClassIndex[av['home_team_defenceDefenderLineClass']]) * (defenceDefenderLineClassIndex[av['home_team_defenceDefenderLineClass']] != None))
            newX.append(1 * (i == defenceDefenderLineClassIndex[av['away_team_defenceDefenderLineClass']]) * (defenceDefenderLineClassIndex[av['away_team_defenceDefenderLineClass']] != None))
        for i in range(len(buildUpPlayDribblingClassIndex)):
            newX.append(1 * (i == buildUpPlayDribblingClassIndex[av['home_team_buildUpPlayDribblingClass']]) * (buildUpPlayDribblingClassIndex[av['home_team_buildUpPlayDribblingClass']] != None))
            newX.append(1 * (i == buildUpPlayDribblingClassIndex[av['away_team_buildUpPlayDribblingClass']]) * (buildUpPlayDribblingClassIndex[av['away_team_buildUpPlayDribblingClass']] != None))
        for i in range(len(defenceAggressionClassIndex)):
            newX.append(1 * (i == defenceAggressionClassIndex[av['home_team_defenceAggressionClass']]) * (defenceAggressionClassIndex[av['home_team_defenceAggressionClass']] != None))
            newX.append(1 * (i == defenceAggressionClassIndex[av['away_team_defenceAggressionClass']]) * (defenceAggressionClassIndex[av['away_team_defenceAggressionClass']] != None))
        for i in range(len(buildUpPlayDribblingIndex)):
            newX.append(1 * (i == buildUpPlayDribblingIndex[av['home_team_buildUpPlayDribbling']]) * (buildUpPlayDribblingIndex[av['home_team_buildUpPlayDribbling']] != None))
            newX.append(1 * (i == buildUpPlayDribblingIndex[av['away_team_buildUpPlayDribbling']]) * (buildUpPlayDribblingIndex[av['away_team_buildUpPlayDribbling']] != None))
        for i in range(len(defencePressureClassIndex)):
            newX.append(1 * (i == defencePressureClassIndex[av['home_team_defencePressureClass']]) * (defencePressureClassIndex[av['home_team_defencePressureClass']] != None))
            newX.append(1 * (i == defencePressureClassIndex[av['away_team_defencePressureClass']]) * (defencePressureClassIndex[av['away_team_defencePressureClass']] != None))
        for i in range(len(chanceCreationPositioningClassIndex)):
            newX.append(1 * (i == chanceCreationPositioningClassIndex[av['home_team_chanceCreationPositioningClass']]) * (chanceCreationPositioningClassIndex[av['home_team_chanceCreationPositioningClass']] != None))
            newX.append(1 * (i == chanceCreationPositioningClassIndex[av['away_team_chanceCreationPositioningClass']]) * (chanceCreationPositioningClassIndex[av['away_team_chanceCreationPositioningClass']] != None))
        for i in range(len(buildUpPlayPassingClassIndex)):
            newX.append(1 * (i == buildUpPlayPassingClassIndex[av['home_team_buildUpPlayPassingClass']]) * (buildUpPlayPassingClassIndex[av['home_team_buildUpPlayPassingClass']] != None))
            newX.append(1 * (i == buildUpPlayPassingClassIndex[av['away_team_buildUpPlayPassingClass']]) * (buildUpPlayPassingClassIndex[av['away_team_buildUpPlayPassingClass']] != None))
        for i in range(len(defenceTeamWidthClassIndex)):
            newX.append(1 * (i == defenceTeamWidthClassIndex[av['home_team_defenceTeamWidthClass']]) * (defenceTeamWidthClassIndex[av['home_team_defenceTeamWidthClass']] != None))
            newX.append(1 * (i == defenceTeamWidthClassIndex[av['away_team_defenceTeamWidthClass']]) * (defenceTeamWidthClassIndex[av['away_team_defenceTeamWidthClass']] != None))
        for i in range(len(buildUpPlayPositioningClassIndex)):
            newX.append(1 * (i == buildUpPlayPositioningClassIndex[av['home_team_buildUpPlayPositioningClass']]) * (buildUpPlayPositioningClassIndex[av['home_team_buildUpPlayPositioningClass']] != None))
            newX.append(1 * (i == buildUpPlayPositioningClassIndex[av['away_team_buildUpPlayPositioningClass']]) * (buildUpPlayPositioningClassIndex[av['away_team_buildUpPlayPositioningClass']] != None))
        for i in range(len(defenceAggressionClassIndex)):
            newX.append(1 * (i == defenceAggressionClassIndex[av['home_team_defenceAggressionClass']]) * (defenceAggressionClassIndex[av['home_team_defenceAggressionClass']] != None))
            newX.append(1 * (i == defenceAggressionClassIndex[av['away_team_defenceAggressionClass']]) * (defenceAggressionClassIndex[av['away_team_defenceAggressionClass']] != None))
        for i in range(len(defenceDefenderLineClassIndex)):
            newX.append(1 * (i == defenceDefenderLineClassIndex[av['home_team_defenceDefenderLineClass']]) * (defenceDefenderLineClassIndex[av['home_team_defenceDefenderLineClass']] != None))
            newX.append(1 * (i == defenceDefenderLineClassIndex[av['away_team_defenceDefenderLineClass']]) * (defenceDefenderLineClassIndex[av['away_team_defenceDefenderLineClass']] != None))
            
        
'''
