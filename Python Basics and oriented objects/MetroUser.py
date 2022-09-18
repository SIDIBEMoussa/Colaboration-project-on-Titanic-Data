import random, time
import datetime
class MetroUser():

    def __init__(self, name, dateOfBirth, adress, clientID , nbTraject, balance):
        self.name, self.dateOfBirth, self.adress, self.clientID, self.nbTraject, self.balance = name, dateOfBirth, adress, clientID , nbTraject, balance
        self.buyHistory = {}


    def buyTicket(self, price, stationName):
        if price <= self.balance : 
            self.nbTraject +=1
            self.balance -= price
            if stationName  in self.buyHistory .keys() :self.buyHistory [stationName] +=1
            else: self.buyHistory [stationName] =1
            return True
        else: return False

            
    def moveOut(self, newAdress): self.adress= newAdress

    @classmethod
    def generateClientID(cls):
        id = ""
        for _ in range(10): id+= str(random.randint(0,9))
        return id

    def getUserData(self):
        userData = {
            "name":self.name,
            "dateOfBirth":self.dateOfBirth,
            "adress":self.adress,
            "clientId":self.clientID,
            "nbTraject": self.nbTraject,
            "balance":self.balance,
            "history":self.buyHistory, 
        }
        return userData

    def getUserHistory(self): return self.buyHistory 