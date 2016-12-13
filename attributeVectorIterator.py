from collections import defaultdict, deque
import sqlite3
from datetime import datetime, timedelta
import copy
from StringIO import StringIO


"""
N.B. Class mixes class and instance variables and treats them all as instance variables.
     Usage should restrict to only having one of these iterators at a time.
"""
class attributeVectorIterator(object):

    '''
    Some constants used for config
    '''
    gameHistoryLength = 5
    sqlDateFormat = '%Y-%m-%d %H:%M:%S'


    '''
    Tables to keep track of meta-data read from the database
    One entry per team
    lastMatchDate is used to compute the time since a teams last match
    gameHistory is used to keep track of WDL history, W=1, D=0, L=-1
    pointTable keeps track of the points table
    '''
    league = ''
    currentSeason = ''
    teamList = []
    lastMatchDate = {}
    gameHistory = {}
    pointTable = {}


    '''
    Connection and cursor to the database, and some SQL values to remember
    Need to remember leagueID to get the teams for each season
    dbConn is our persistent connection to the database, which we can grab 'cursors' to access data
    dbMatchCursor is our cursor for the match table we are an iterator for
    '''
    leagueID = 0
    databaseName = ''
    dbConn = None
    dbMatchCursor = None


    '''
    Constructor initialises a connection to the database and fills out
    initial values in the meta data
    
    In the database connection we set sqlite3.Row as the row factory, to make 
    '''
    def __init__(self, years=['2012/2013','2013/2014','2014/2015'], league = 'England Premier League', databaseName = "database.sqlite"):

        self.databaseName = databaseName
        self.league = league
        self.currentSeason = years[0]

        # Setup the database connection, we only need one of these
        #self.dbConn = sqlite3.connect(databaseName)
        #self.dbConn.row_factory = sqlite3.Row
        
        tempConn = sqlite3.connect(databaseName)
        tempfile = StringIO()
        for line in tempConn.iterdump():
            tempfile.write('%s\n' % line)
        tempConn.close()
        tempfile.seek(0)

        self.dbConn = sqlite3.connect(":memory:")
        self.dbConn.cursor().executescript(tempfile.read())
        self.dbConn.commit()
        self.dbConn.row_factory = sqlite3.Row

        # Temp sql connection, used to grab some initial data
        tempCursor = self.dbConn.cursor()
        tempCursor.execute('SELECT id FROM League WHERE name = "{0}"'.format(self.league))
        self.leagueID = tempCursor.fetchone()[0]

        # Get the list of teams
        self.newSeasonSetup()

        # Setup the connection to use
        # Set connection to use sqlite3.Row as a row factory
        # sqlite3.Row is an object that can be indexed by column name, indexed by a number etc. 
        queryString = ''
        if len(years) > 1:
            queryString = 'SELECT * FROM Match WHERE league_id = {0} AND season IN {1} ORDER BY date'.format(self.leagueID, str(tuple(years)))  
        else:
            queryString = 'SELECT * FROM Match WHERE league_id = {0} AND season = "{1}" ORDER BY date'.format(self.leagueID, str(years[0]))
        self.dbMatchCursor = self.dbConn.cursor()
        self.dbMatchCursor.execute(queryString)


    ''' 
    Allow the class to be used in generator expressions
    '''
    def __iter__(self):
        return self

    '''
    Get the next (attribute item, label) pair from the iterable (us)
    '''
    def next(self):
        # Get the next match row
        matchRow = self.dbMatchCursor.fetchone()

        # If it's None, then we're finished, close any database connections, and raise StopIteration
        if matchRow == None:
            self.dbConn.close()
            raise StopIteration()

        # Check if we are into a new season
        if matchRow['season'] != self.currentSeason:
            self.currentSeason = matchRow['season']
            self.newSeasonSetup()
        
        # Get team names and dates
        homeTeamApiID = matchRow['home_team_api_id']
        awayTeamApiID = matchRow['away_team_api_id']
        date = datetime.strptime(matchRow['date'], self.sqlDateFormat)
        tempCursor = self.dbConn.cursor()
        tempCursor.execute('SELECT team_long_name FROM Team WHERE team_api_id = {0}'.format(homeTeamApiID))
        homeTeamName = tempCursor.fetchone()[0]
        tempCursor.execute('SELECT * FROM Team_Attributes WHERE team_api_id = {0} AND date < "{1}" ORDER BY date DESC'.format(homeTeamApiID, matchRow['date']))
        homeTeamAttributesRow = tempCursor.fetchone()
        tempCursor.execute('SELECT team_long_name FROM Team WHERE team_api_id = {0}'.format(awayTeamApiID))
        awayTeamName = tempCursor.fetchone()[0]
        tempCursor.execute('SELECT * FROM Team_Attributes WHERE team_api_id = {0} AND date < "{1}" ORDER BY date DESC'.format(awayTeamApiID, matchRow['date']))
        awayTeamAttributesRow = tempCursor.fetchone()

        # Create attribute vector, make it a defaultdict(float) so values default to 0.0 in a sparse vector
        # Match info will make subsequent calls to add player info and info from meta data
        attrVector = {}
        self.addMatchInfo(attrVector, matchRow, homeTeamName, homeTeamAttributesRow, awayTeamName, awayTeamAttributesRow, date) 

        # Also get the match result, i.e. the label
        homeScore = matchRow['home_team_goal']
        awayScore = matchRow['away_team_goal']
        matchScore = (homeScore, awayScore)

        # Update the meta data
        self.updateMetaData(homeTeamName, homeScore, awayTeamName, awayScore, date)

        # Return the training pair
        return (attrVector, matchScore)

    '''
    Every new season the meta data will need to reset. Teams are premoted/demoted, the points and game history can be reset
    '''
    def newSeasonSetup(self):
        tempCursor = self.dbConn.cursor()

        # Get the list of teams
        self.teamList = []
        teamNameQuery = ('SELECT DISTINCT team_long_name '
                         'FROM Team, Match '
                         'WHERE Team.team_api_id = Match.home_team_api_id '
                         '  AND season = "{0}" '
                         '  AND Match.league_id = {1} ')
        for team in tempCursor.execute(teamNameQuery.format(self.currentSeason, self.leagueID)):
            self.teamList.append(team[0])

        # Reset the stats for each table
        self.lastMatchDate = {}
        self.pointTable = defaultdict(int)
        self.gameHistory = defaultdict(deque)

    '''
    Add all information from a row in Match table and the current meta data
    This also updates the meta data
    '''
    def addMatchInfo(self, attrVector, matchRow, homeTeamName, homeTeamAttributesRow, awayTeamName, awayTeamAttributesRow, date):
        # Add the team's names as attributes, one hot encoding
        attrVector['homeTeamName-'+homeTeamName] = 1
        attrVector['awayTeamName-'+awayTeamName] = 1

        # Compute the home and away formations 
        self.addFormation(attrVector, matchRow, 'home')
        self.addFormation(attrVector, matchRow, 'away')

        # Add in a value for their current standing in the league
        # Their game history to model form
        # Their time since last match to model fatigue
        attrVector['homeLeaguePosition'] = self.leaguePosition(homeTeamName)
        attrVector['awayLeaguePosition'] = self.leaguePosition(awayTeamName)
        attrVector['homeGameHistoryScore'] = self.computeGameHistoryScore(homeTeamName)
        attrVector['awayGameHistoryScore'] = self.computeGameHistoryScore(awayTeamName)
        attrVector['homeTimeSinceLastMatch'] = self.timeSinceLastMatch(homeTeamName, date)
        attrVector['awayTimeSinceLastMatch'] = self.timeSinceLastMatch(awayTeamName, date)
        
        # Add in information about the two teams
        self.addTeamAttributes(attrVector, 'home', homeTeamAttributesRow)
        self.addTeamAttributes(attrVector, 'away', awayTeamAttributesRow)
        
        # Add in information about each player
        tempCursor = self.dbConn.cursor()
        for homeOrAway in ['home', 'away']:
            for i in range(1,12):
                playerStr = homeOrAway + '_player_' + str(i)
                prefix = playerStr + '_'
                if matchRow[playerStr] == None: continue # TODO: Solve this <--- problem
                tempCursor.execute('SELECT * FROM Player WHERE player_api_id = {0}'.format(matchRow[playerStr]))
                playerRow = tempCursor.fetchone()
                self.addPlayerValues(attrVector, prefix, playerRow, date)
                tempCursor.execute('SELECT * FROM Player_Attributes WHERE player_api_id = {0} AND date < "{1}" ORDER BY date DESC'.format(matchRow[playerStr] , matchRow['date']))
                playerAttributesRow = tempCursor.fetchone()
                self.addPlayerAttributes(attrVector, prefix, playerAttributesRow)
        



    '''
    From a match row, computes the formations (using the Y coordinates of player positions) and add's them as an attribute
    Note that we start at player 2, and loop from 3 to 11 because we ignore the goalkeeper
    Code is quite 'hacky' sorry, but it does produce the correct thing
    '''
    def addFormation(self, attrVector, matchRow, homeOrAway):
        # Format some strings to pull the correct data out from the row
        baseStr = homeOrAway + '_player_Y{0}'
        formation = []
        lastY = matchRow[baseStr.format(2)]
        count = 1
        for i in range(3, 12):
            nextY = matchRow[baseStr.format(i)]
            if i == 11:
                if nextY == lastY:
                    formation.append(count+1)
                else:
                    formation.append(count)
                    formation.append(1)
            elif nextY != lastY:
                formation.append(count)
                count = 0
            count += 1
            lastY = nextY
        
        # Add the attribute!
        attrString = homeOrAway + 'Formation'
        formationString = ''
        for rowCount in formation:
            if formationString == '': formationString += str(rowCount)
            else: formationString += '-' + str(rowCount)
        attrVector[attrString+'-'+formationString] = 1



    '''
    Computing the league position for the given team at the current time
    Need to take a copy of the pointsTable to condition on. Because if we access table[key] in a deafult dict where
    the key didn't exist before, it creates the value for table[key]. This changes the table and causes a runtime 
    error
    '''
    def leaguePosition(self, teamName):
        pointTableCpy = copy.copy(self.pointTable)
        return 1 + sum([1 for otherTeamName in self.pointTable if pointTableCpy[otherTeamName] > pointTableCpy[teamName]])



    '''
    Compute a value from the game history representing how we'll they've done
    For now, with win=1, draw=0, loss=-1 we just add these together
    '''
    def computeGameHistoryScore(self, teamName):
        return sum(self.gameHistory[teamName])



    '''
    Compute the time since the last match a team has played
    If no value in last match, then default to 0, so that the weight for this value has no effect
    deltaTime is a datetime.timeDelta object
    '''
    def timeSinceLastMatch(self, teamName, date):
        lastDate = self.lastMatchDate.get(teamName, None)
        if lastDate == None: return 0
        deltaTime = date - lastDate
        return deltaTime.total_seconds()



    '''
    Add attributes for the home/away team from their row in the database
    '''
    def addTeamAttributes(self, attrVector, homeOrAway, teamAttributesRow):
        prefix = homeOrAway + '_team_'
        columns = ['buildUpPlaySpeed', 'buildUpPlayDribbling', 'buildUpPlayDribblingClass', 'buildUpPlayPassing', 
                   'buildUpPlayPassingClass', 'buildUpPlayPositioningClass', 'chanceCreationPassing', 
                   'chanceCreationPassingClass', 'chanceCreationCrossing', 'chanceCreationCrossingClass', 
                   'chanceCreationShooting', 'chanceCreationShootingClass', 'chanceCreationPositioningClass', 
                   'defencePressure', 'defencePressureClass', 'defenceAggression', 'defenceAggressionClass', 
                   'defenceTeamWidth', 'defenceTeamWidthClass', 'defenceDefenderLineClass']
        self.copyRowValuesToAttrVector(attrVector, prefix, columns, teamAttributesRow)



    '''
    Add values for a given player. These are things that don't change, like height, weight, date of birth
    We pass in the date of the match to compute the age
    '''
    def addPlayerValues(self, attrVector, prefix, playerRow, date):
        attrVector[prefix+'height'] = playerRow['height']
        attrVector[prefix+'weight'] = playerRow['weight']
        birthdate = datetime.strptime(playerRow['birthday'], self.sqlDateFormat)
        age = date - birthdate
        attrVector[prefix+'dob'] = age.total_seconds()



    '''
    Add attributes for a given player
    '''
    def addPlayerAttributes(self, attrVector, prefix, playerAttributesRow):
        columns = ['overall_rating', 'potential, preferred_foot', 'attacking_work_rate', 'defensive_work_rate', 
                   'crossing', 'finishing', 'heading_accuracy', 'short_passing', 'volleys', 'dribbling', 'curve', 
                   'free_kick_accuracy', 'long_passing', 'ball_control', 'acceleration', 'sprint_speed', 'agility', 
                   'reactions', 'balance', 'shot_power', 'jumping', 'stamina', 'strength', 'long_shots', 'aggression', 
                   'interceptions', 'positioning', 'vision', 'penalties', 'marking', 'standing_tackle', 'sliding_tackle', 
                   'gk_diving', 'gk_handling', 'gk_kicking', 'gk_positioning', 'gk_reflexes']
        self.copyRowValuesToAttrVector(attrVector, prefix, columns, playerAttributesRow)



    '''
    General method to copy all values from a row to the attribute vector, with a given prefix for the attribute dict key
    Taking care to perform one hot encoding on non numeric values, and also taking care to ignore None values
    '''
    def copyRowValuesToAttrVector(self, attrVector, prefix, columns, row):
        for col in columns:
            if col in row.keys():
                if isinstance(row[col], (int, float)):
                    attrVector[prefix+"-"+col] = row[col]
                elif isinstance(row[col], (str, unicode)):
                    attrVector[prefix+"-"+col+"-"+row[col]] = 1



    ''' 
    Update meta data
    '''
    def updateMetaData(self, homeTeam, homeTeamScore, awayTeam, awayTeamScore, date):
        self.lastMatchDate[homeTeam] = date
        self.lastMatchDate[awayTeam] = date

        if homeTeamScore > awayTeamScore:
            self.pointTable[homeTeam] += 3
            self.pushResultOnHistory(homeTeam, 1)
            self.pushResultOnHistory(awayTeam, -1)
        elif homeTeamScore < awayTeamScore:
            self.pointTable[awayTeam] += 3
            self.pushResultOnHistory(homeTeam, -1)
            self.pushResultOnHistory(awayTeam, 1)
        else:
            self.pointTable[homeTeam] += 1
            self.pointTable[awayTeam] += 1
            self.pushResultOnHistory(homeTeam, 0)
            self.pushResultOnHistory(awayTeam, 0)



    ''' 
    Updating the history of a team after a game has been played
    '''
    def pushResultOnHistory(self, team, result):
        self.gameHistory[team].append(result)
        if len(self.gameHistory[team]) > self.gameHistoryLength:
            self.gameHistory[team].popleft()
            

