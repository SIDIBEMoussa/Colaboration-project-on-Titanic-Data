import MetroUser
from datetime import datetime
from datetime import date


class MetroStation():

    def __init__(self, name, fullTicketPrice, reduceTicketPrice):
        self.name= name
        self.userList = []
        self.userIDList = []
        self.reducePriceTicketSold= 0
        self.fullPriceTicketSold = 0
        self.fullTicketPrice, self.reduceTicketPrice = fullTicketPrice, reduceTicketPrice

    def addUser(self, userData):
        name, dateOfBirth, adress, clientID , nbTraject, balance = self.decodeUserData(userData)
        if not clientID in self.userIDList: 
            self.userList.append(MetroUser.MetroUser(name, dateOfBirth, adress, clientID , nbTraject, balance ))
            self.userIDList.append(clientID)
        else:
            while clientID in self.userIDList: clientID = MetroUser.generateClientID()
            self.userList.append(MetroUser(name, dateOfBirth, adress, clientID , nbTraject, balance ))
            self.userIDList.append(clientID)
        



    def decodeUserData(self, userData):
        splited = userData.split("-")
        # for val in splited : print(val)
        name= splited[0].split(":")[1].strip()
        dateOfBirth= datetime.strptime(splited[2].split(":")[1].strip(), '%Y/%m/%d')
        adress = splited[1].split(":")[1]
        if not "id" in splited[3] : clientID = MetroUser.MetroUser.generateClientID()
        else: clientID = splited[3].split[1].strip()
        nbTraject  = int(splited[4].split()[0].strip())
        balance = int(splited[-1].strip())
        return name, dateOfBirth, adress, clientID , nbTraject, balance

    def getMetroData(self):
        metroData = {}
        for user in self.userList:
            userData ={"stationName": self.name}
            ticketPrice = self.reduceTicketPrice
            today = date.today()
            age = today.year - user.dateOfBirth.year - ((today.month, today.day) < (user.dateOfBirth.month, user.dateOfBirth.day))
            if age >= 26 : ticketPrice = self.fullTicketPrice
            userData =userData  | user.getUserData().pop("history")
            nbTicketSolde = 0
            if self.name in user.getUserHistory().keys(): nbTicketSold = user.getUserHistory()[self.name]
            userData["ticketPrice"] = ticketPrice
            userData["nbTicketBought"] = nbTicketSold
            metroData[user.clientID] = userData
        return metroData

    def sellTicket(self, user):
        today = date.today()
        age = today.year - user.dateOfBirth.year - ((today.month, today.day) < (user.dateOfBirth.month, user.dateOfBirth.day))
        if age >= 26 and user.buyTicket(self.fullTicketPrice, self.name): self.fullPriceTicketSold +=1
        elif age < 26 and user.buyTicket(self.reduceTicketPrice, self.name) : self.reducePriceTicketSold +=1


    def getDaylyRecet(self):
        return self.reducePriceTicketSold* self.reduceTicketPrice + self.fullPriceTicketSold * self.fullTicketPrice