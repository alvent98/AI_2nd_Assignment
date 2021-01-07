import os, sys, math


def bayes(data, Ve):
    #Ve = target email
    #c = counter of the examples of each category
    c=[0,0]
    for i in range(len(data)):            
        if data[i][1000] == 0:
            c[0] = c[0] + 1.0
        if data[i][1000] == 1:
            c[1] = c[1] + 1.0

    #print(c)
    #product of possibilities
    product = [1,1]

    #counter = counter of emails in training dataset that have the same value with target email (Ve) in a feature
    counter = [0 for x in range(0,1000)]
    #denom = sum of target email features and the number of email of each category in data
    denom = [0 for x in range(0,1000)]
    for pos_c in range(len(c)):
        #print ("Entered ", pos_c, "loop of c")
        for pos_row_data in range(len(data)):
            if(data[pos_row_data][1000]) == pos_c:
                for pos_Ve in range (len(Ve)):
                    if data[pos_row_data][pos_Ve] == Ve[pos_Ve]:
                        counter[pos_Ve] += 1

        for pos_row_data in range(len(counter)):
            counter[pos_row_data] += 1

        for pos_row_data in range(len(Ve)):
            denom[pos_row_data] = len(Ve) + c[pos_c]
        #print ("counter: ", counter)
        #print ("denom: ", denom)

        for pos_row_data in range(len(counter)):
            product[pos_c] *= counter[pos_row_data]/denom[pos_row_data]
        #print ("product: ", product[pos_c])

        counter = [0 for x in range(0,1000)]
        denom = [0 for x in range(0,1000)]
    pos_max = product.index(max(product))
    print ("Most possibly (", max(product)*100,"%) it belongs at ", pos_max)


#This function gets as params the two paths (spams and hams), and creates two dictionaries, one with the
#words that appear in ham emails and one other with those that appear in spam emails.
def lexiko(hamPath,spamPath):
    source_code_path = os.getcwd()

    os.chdir(spamPath)
    spamDirs = os.listdir(spamPath)
    lexiko.spamDict = {}
    enc = "iso-8859-15"
    lexiko.countofspams = len(spamDirs)
    #Tokenize the words in spam emails:
    for file in spamDirs:
        myfile = open(file, "r", encoding=enc)
        for line in myfile:
            for word in line.split():
                if word in lexiko.spamDict:
                    lexiko.spamDict[word] += 1
                else:
                    lexiko.spamDict[word] = 1

    os.chdir(hamPath)
    hamDirs = os.listdir(hamPath)
    lexiko.countofhams = len(hamDirs)
    lexiko.hamDict = {}
    #Tokenize the words in ham emails:
    for file in hamDirs:
        myfile = open(file)
        for line in myfile:
            for word in line.split():
                if word in lexiko.hamDict:
                    lexiko.hamDict[word] += 1
                else:
                    lexiko.hamDict[word] = 1

    os.chdir(source_code_path)

#This function creates the 1000 values' list with the most useful word in the emails
def IGgetter(hamDict,spamDict):

    mainDict = {}

    sum = (lexiko.countofspams + lexiko.countofhams)
    spamRatio = lexiko.countofspams / sum #P(C=1)
    print("Spam ratio is: ",spamRatio)
    hamRatio = lexiko.countofhams / sum #P(C=0)
    H = -spamRatio*math.log(spamRatio, 2) - hamRatio * math.log(hamRatio, 2)

    #Fill the main Dictionary with the words in the ham emails.
    for i in hamDict:
        hamDict[i] /= float(lexiko.countofhams)
        if i in mainDict:
            mainDict[i] += hamDict[i]
        else:
            mainDict[i] = hamDict[i]

    #Fill the main Dictionary with the words in the spam emails.
    for i in spamDict:
        spamDict[i] /= float(lexiko.countofspams)
        if i in mainDict:
            mainDict[i] += spamDict[i]
        else:
            mainDict[i] = spamDict[i]

    #Convert the numbers in main Dictionary, from number of appearences of each word, 
    #to percentage of appearences out of the total number of emails.
    for i in mainDict:
        mainDict[i] /= float(sum) #P(X=1)

    #print(lexiko.spamDict["Subject:"])

    print("MainDict len is :",len(mainDict))
    print("spamDict len is :",len(spamDict))
    print("hamDict len is :",len(hamDict))
    interLex = {} #internal Lexicon
    hamInveInterLex = {} #ham inverted internal lexicon
    spamInveInterLex = {} #spam inverted internal lexicon
    HX0 = {} #H(C|X=0)
    HX1 = {} #H(C|X=1)

    #Normalize abnormal values in mainDict.
    for i in mainDict:
        if mainDict[i] >= 1: #Some values may appear more than once in all the emails (E.g. comma, "a" etc)
            mainDict[i] = 0.999

    #Normalize abnormal values in hamDict, and add missing keys.
    for i in hamDict:
        if hamDict[i] >= 1: hamDict[i] = 0.999
        if i not in spamDict: spamDict[i] = 0.0001

    #Normalize abnormal values in spamDict, and add missing keys.
    for i in spamDict:
        if spamDict[i] >= 1: spamDict[i] = 0.999
        if i not in hamDict: hamDict[i] = 0.0001

    counter = 0
    for i in hamDict:
        if hamDict[i] >=1 or hamDict[i] <=0:
            counter += 1

    #print("hamDict items that are abnormal: ", counter)

    counter = 0
    for i in spamDict:
        if spamDict[i] >=1 or spamDict[i] <=0:
            counter += 1

    #print("spamDict items that are abnormal: ", counter)

    counter = 0
    for i in mainDict:
        if mainDict[i] >=1 or mainDict[i] <=0:
            counter += 1

    #print("mainDict items that are abnormal: ", counter)

    #P(C=1|X=0) = P(C=1) * P(X=0|C=1) / (1 - P(X=1))
    for i in spamDict:
        interLex[i] = 1.0 - spamDict[i]
        spamInveInterLex[i] = spamRatio * interLex[i] /(1.0 - mainDict[i]) #P(C=1|X=0)

    #P(C=0|X=0) = P(C=0) * P(X=0|C=0) / (1 - P(X=1))
    for i in hamDict:
        interLex[i] = 1.0 - hamDict[i]
        hamInveInterLex[i] = hamRatio * interLex[i] /(1.0 - mainDict[i]) #P(C=0|X=0)

    del interLex

    for i in mainDict: #H(C|X=0) = -P(C=1|X=0)*log2(P(C=1|X=0)) - P(C=0|X=0)*log2(P(C=0|X=0))
        HX0[i] = -hamInveInterLex[i]*math.log(hamInveInterLex[i], 2) -spamInveInterLex[i]*math.log(spamInveInterLex[i], 2)

    hamInveInterLex = {}
    spamInveInterLex = {}

    #P(C=1|X=1) =  P(C=1) * P(X=1|C=1) / P(X=1)
    for i in spamDict:
        spamInveInterLex[i] = spamRatio * spamDict[i] /mainDict[i] #P(C=1|X=1)

    #P(C=0|X=1) =  P(C=0) * P(X=1|C=0) / P(X=1)
    for i in hamDict:
        hamInveInterLex[i] = hamRatio * hamDict[i] /mainDict[i] #P(C=0|X=1)

    #H(C|X=1) = -P(C=1|X=1)*log2(P(C=1|X=1)) - P(C=0|X=1)*log2(P(C=0|X=1))
    for i in mainDict:
        HX1[i] = -hamInveInterLex[i]*math.log(hamInveInterLex[i], 2) -spamInveInterLex[i]*math.log(spamInveInterLex[i], 2)

    IG = {}
    #IG = H - P(X = 1)*H(C|X=1) - P(X = 0)*H(C|X=0)
    for i in mainDict:
        IG[i] = H - mainDict[i]*HX1[i] - (1 - mainDict[i])*HX0[i] 

    IG = sorted(IG, key = IG.__getitem__,reverse = True)
    IGgetter.mostUsefulWords = []
    counter = 0
    for i in IG:
        IGgetter.mostUsefulWords.append(IG[counter])
        counter += 1
        if counter >= 1000 : break

    '''
    IG = H - P(X = 1)*H(C|X=1) - P(X = 0)*H(C|X=0)

    H(C|X=1) = -P(C=1|X=1)*log2(P(C=1|X=1)) - P(C=0|X=1)*log2(P(C=0|X=1))

    P(X=1|C=1) <-- this info is at spamDict  = P(X=1) * P(C=1|X=1) / P(C=1)
    P(X=1|C=0) <-- this info is at hamDict   = P(X=1) * P(C=0|X=1) / P(C=0)

    H(C|X=0) = -P(C=1|X=0)*log2(P(C=1|X=0)) - P(C=0|X=0)*log2(P(C=0|X=0))

    P(X=1|C=1) = 1 - P(X=0|C=1) <=> P(X=0|C=1) = 1 - P(X=1|C=1)
    1o Vima:
        P(X=0|C=1) = 1 - P(X=1|C=1)
        P(C=1|X=0) = P(C=1) * P(X=0|C=1) / (1 - P(X=1))
    2o Vima:
        P(X=0|C=0) = 1 - P(X=1|C=0)
        P(C=0|X=0) = P(C=0) * P(X=0|C=0) / (1 - P(X=1))
    3o Vima:
        P(C=1|X=1) =  P(C=1) * P(X=1|C=1) / P(X=1) 
    4o Vima:
        P(C=0|X=1) =  P(C=0) * P(X=1|C=0) / P(X=1) 
    '''

def training(hamPath,spamPath):
    source_code_path = os.getcwd()

    os.chdir(spamPath)
    spamDirs = os.listdir(spamPath)
    enc = "iso-8859-15"
    w = 1001
    h = 1832

    training.data = [[0 for x in range(w)] for y in range(h)] 
    for i in range(0,1832):
        for j in range(0,1001):
            training.data[i][j] = 0
    
    i = 0
    for file in spamDirs:
        if "2004" in file: 
            myfile = open(file, "r", encoding=enc)
            for line in myfile:
                for word in line.split():
                    if word in IGgetter.mostUsefulWords:
                        position = IGgetter.mostUsefulWords.index(word)
                        training.data[i][position] = 1
            training.data[i][1000] = 1
            i += 1

    training.spamsInTraining = i
    #print("The i, after the reading of the spams, is: ", training.spamsInTraining)

    os.chdir(hamPath)
    hamDirs = os.listdir(hamPath)
    #The hams with the token "2000" are 2233
    #The spams with the token "2004" are 916
    #The total is 3149
    
    i = 0
    for file in hamDirs:
        if "2000" in file: 
            myfile = open(file)
            for line in myfile:
                for word in line.split():
                    if word in IGgetter.mostUsefulWords:
                        position = IGgetter.mostUsefulWords.index(word)
                        training.data[i][position] = 1
            i += 1
        if i == training.spamsInTraining: break

    training.hamsInTraining = i
    #print("The i, after the reading of the hams, is: ",training.hamsInTraining)

def targetEmail(emailName,path):
    targetEmail.features  = [0 for y in range(1000)]
    source_code_path = os.getcwd()
    os.chdir(path)
    enc = "iso-8859-15"
    myfile = open(emailName, "r", encoding=enc)
    for line in myfile:
        for word in line.split():
            if word in IGgetter.mostUsefulWords:
                position = IGgetter.mostUsefulWords.index(word)
                targetEmail.features[position] = 1

#run function lexiko (See above)
hamPath = r"C:\Users\a\PycharmProjects\enron1\ham"
spamPath = r"C:\Users\a\PycharmProjects\enron1\spam"
lexiko(hamPath, spamPath)
#run function IGgetter (See above)
IGgetter(lexiko.hamDict,lexiko.spamDict)
#print(len(IGgetter.mostUsefulWords))
training(hamPath,spamPath)

print("Total of hams and spams: ", len(training.data))

'''
counter1 = 0
for i in range(0,1001):
    if training.data[0][i] == 1: counter1 += 1
print("In the first line, found ", counter1, " ones")

counter1 = 0
for i in range(0,1001):
    if training.data[1][i] == 1: counter1 += 1
print("In the second line, found ", counter1, " ones")

counter1 = 0
for i in range(0,1001):
    if training.data[2][i] == 1: counter1 += 1
print("In the third line, found ", counter1, " ones")

counter1 = 0
for i in range(0,1001):
    if training.data[3][i] == 1: counter1 += 1
print("In the fourth line, found ", counter1, " ones")
'''

#emailName = "0007.1999-12-14.farmer.ham.txt"
emailName = "0054.2003-12-21.GP.spam.txt"

targetEmail(emailName,spamPath)

bayes(training.data,targetEmail.features)

