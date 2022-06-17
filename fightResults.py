import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service

options = FirefoxOptions()

opt = input('Launch program headless (y/n): ').lower()
if opt == 'y':
    options.add_argument("--headless")
options.add_argument("--mute-audio")
service = Service(log_path=os.path.devnull)
driver = webdriver.Firefox(options=options, service=service)


def updateStats(winChar, lossChar):
    line = winChar + '|' + lossChar
    matchRes = open('matchResults.txt','a')

    if fightsRecorded > 0:
        end = time.time()
        timeVar = '|'+str(end-start)
        line += timeVar
    matchRes.write(line)
    matchRes.write('\n')
    matchRes.close()


def getCharacters():
    chars = []
    chars.append(driver.find_element(By.XPATH , "/html/body/div/div[1]/div[1]/span/strong").text)
    chars.append(driver.find_element(By.XPATH , "/html/body/div/div[1]/div[2]/span/strong").text)

    return chars

def getPercentage(char, enChar):
    chance = 0
    totalTime = 0
    timesMeasured = 0

    matchRes = open('matchResults.txt','r').read().splitlines()

    totalAverage = 0
    totalAverageMeasured = 0
    for i in matchRes:
        line = i.split('|')   #Getting the average of all timed fights
        if len(line) == 3:
            totalAverage += float(line[2])
            totalAverageMeasured += 1
            
    for line in matchRes:
        lines = line.split('|')
        if lines[0] == char:
            chance += 0.5
            if len(lines) == 3:
                totalTime += float(lines[2]) #Getting a basic sum of results and losses for chance
                timesMeasured += 1 
        elif lines[1] == char:
            chance -= 0.5

    for i in matchRes:
        fighters = i.split('|')
        if fighters[1] == enChar:
            for x in matchRes:
                fighters1 = x.split('|')
                if fighters1[0] == char and fighters1[1] == fighters[0]: #Checking if fighter has beaten another
                    chance += 3                                          #fighter who has beaten the current opponent
    
    if timesMeasured > 0:
        totalAverage = totalAverage/totalAverageMeasured
        averageTime = totalTime/timesMeasured            #Getting the average time of fighter 
        dTime = averageTime-totalAverage-80                #and comparing it to average of all timed fights
        if dTime< 0:
            dTime *= -1
            timePower = 30                 #Decides how much of a difference to the chance the time will make
            chance += (dTime/timePower)    #High timePower = lowChance
        

    return chance

driver.get('https://www.saltybet.com/')
print('Loaded saltybet.com')

fightsRecorded = 0
betRecorded = True
timeRecorded = False

while True:
    time.sleep(5)
    try:
        betStatus = driver.find_element(By.ID, "betstatus").text
    except:
        continue
    
    if 'Payouts' in betStatus and betRecorded == False:
        betRecorded = True
        timeRecorded = False
        recordFights = True
        
        if 'Payouts to Team Red' in betStatus:
            updateStats(chars[0],chars[1])
            print(chars[0] + ' wins against ' + chars[1])

        elif 'Payouts to Team Blue' in betStatus:
            updateStats(chars[1],chars[0])
            print(chars[1] + ' wins against ' + chars[0])

        fightsRecorded += 1


    elif 'Bets are locked' in betStatus and betRecorded == True:
        betRecorded = False

        try:
            chars = getCharacters()
        except:
            continue
        os.system('cls')
        redPercent = str(getPercentage(chars[0],chars[1]))
        bluePercent = str(getPercentage(chars[1],chars[0]))
        
        print('Fights Recorded: ' + str(fightsRecorded))
        print('Current Fight: ' + chars[0] + '(' +redPercent+ ') vs ' + chars[1] + '(' + bluePercent + ')')


    if fightsRecorded > 0 and 'Bets are locked' in betStatus and timeRecorded == False:
        timeRecorded = True
        start = time.time()
        
