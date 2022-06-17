import os, time, sys
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
driver = webdriver.Firefox(options=options, service =service)


def Login(): #login as cookies are not kept
    print('Attempting Login')
    email = '[USERNAME]'
    password = '[[PASSWORD]]'
    time.sleep(5)

    #click login button
    driver.find_element(by=By.CSS_SELECTOR, value='.nav-text > a:nth-child(1) > span:nth-child(1)').click()

    driver.find_element(By.ID, "email").send_keys(email) #enter email
    driver.find_element(By.ID, "pword").send_keys(password) #enter password
    driver.find_element(by=By.CSS_SELECTOR, value='.submit > input:nth-child(1)').click()
    return


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
            chance += 1 #0.5
            if lines[1] == enChar: #has character beat them already
                chance += 4 #2.5
            if len(lines) == 3:
                totalTime += float(lines[2]) #Getting a basic sum of results and losses for chance and if char has beat enChar before
                timesMeasured += 1

        elif lines[1] == char:
            chance -= 1 


    for i in matchRes:
        fighters = i.split('|')
        if fighters[1] == enChar:
            for x in matchRes:
                fighters1 = x.split('|')
                if fighters1[0] == char and fighters1[1] == fighters[0]: #Checking if fighter has beaten another
                    chance += 2 #1.5                                       #fighter who has beaten the current opponent
    
    if timesMeasured > 0:
        totalAverage = totalAverage/totalAverageMeasured
        averageTime = totalTime/timesMeasured            #Getting the average time of fighter 
        dTime = averageTime-totalAverage                #and comparing it to average of all timed fights
        if dTime< 0:
            dTime *= -1
            timePower = 45 #30             #Decides how much of a difference to the chance the time will make
            chance += (dTime/timePower)    #High timePower = time affects chance less
        

    return chance

def placeBet():
    wagerInput = driver.find_element(By.ID, "wager")
    balance = driver.find_element(By.ID, "balance").text
    balance= balance.replace(',','')

    redName = driver.find_element(By.XPATH , "/html/body/div/div[1]/div[1]/span/strong").text
    redChance = getPercentage(driver.find_element(By.XPATH , "/html/body/div/div[1]/div[1]/span/strong").text,
                              driver.find_element(By.XPATH , "/html/body/div/div[1]/div[2]/span/strong").text)
    
    blueName = driver.find_element(By.XPATH , "/html/body/div/div[1]/div[2]/span/strong").text
    blueChance = getPercentage(driver.find_element(By.XPATH , "/html/body/div/div[1]/div[2]/span/strong").text,
                               driver.find_element(By.XPATH , "/html/body/div/div[1]/div[1]/span/strong").text)
    

    print(redName+'(' + str(redChance) + ') vs ' + blueName + '(' + str(blueChance) + ')')
    baseBet = 8 #starting bet = total balance/betAmount
    

    if redChance >= blueChance:
        betSide = 0
        betAmount = baseBet - (redChance-blueChance)
        betAmount = str(int(round((int(balance)/betAmount),0))) #decide how much to bet, low betAmount = high bet 
        
        wagerInput.send_keys(betAmount)
        driver.find_element(By.ID, "player1").click()

        info = [driver.find_element(By.XPATH , "/html/body/div/div[1]/div[1]/span/strong").text,betAmount]
        return info
        
    elif blueChance > redChance:
        betSide = 1
        betAmount = baseBet - (blueChance-redChance)
        betAmount = str(int(round((int(balance)/betAmount),0))) #decide how much to bet, fraction of balance
        
        wagerInput.send_keys(betAmount)
        driver.find_element(By.ID, "player2").click()

        info = [driver.find_element(By.XPATH , "/html/body/div/div[1]/div[2]/span/strong").text,betAmount]
        return info
    

if 'y' in input('Only bet in tournaments? (y/n): ').lower():
    tournamentMode = True
else:
    tournamentMode = False
driver.get('https://www.saltybet.com/')
try:
    Login()
    driver.find_element(By.ID, "betstatus").text
    print('Login Successful')
except:
    print('Login Failed, Check if login information is correct')
    sys.exit()

alreadyBet = False
matchesBet = 0
os.system('cls')
print('Wating to bet')

while True: #main loop
    time.sleep(5) #check if bets are open every 5 seconds

    try:
        betStatus = driver.find_element(By.ID, "betstatus").text #get bet status
    except:
        pass
    
    if betStatus != 'Bets are OPEN!':
        time.sleep(20)
        alreadyBet = False
        
    if alreadyBet == False and betStatus == 'Bets are OPEN!': #bet on new fight if not done already
        alreadyBet = True
        try:
            os.system('cls')
            print('Login Successful')
            balance = driver.find_element(By.ID, "balance").text.replace(',','')
            
            print('Balance: $'+ str(balance) + '   Games Bet On: ' + str(matchesBet)+'\n')

            if tournamentMode: #Only bet during tournaments
                if '(Tournament Balance)' in driver.find_element(by=By.CSS_SELECTOR, value='#footer-alert').text: #if tournament on
                    info = placeBet() #Get character and amount bet
                    alreadyBet = True
                    print('Current Bet: $' + info[1] + ' on ' + info[0])
                    matchesBet += 1

                else:
                    print('No tournament currently running')

                    
            else: #Bet on every fight
                info = placeBet() #Get character and amount bet
                alreadyBet = True
                print('Current Bet: $' + info[1] + ' on ' + info[0])
                matchesBet += 1

        except Exception as e:
            print('\nError Placing Bet')
            print(e)
            
