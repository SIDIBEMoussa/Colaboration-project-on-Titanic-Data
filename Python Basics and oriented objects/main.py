import MetroUser
import MetroStation
import random
import names
import pandas as pd


def main():
    saintPaul = MetroStation.MetroStation("Saint Paul", 1.7, 0.7)
    print("generating random users")
    for _ in range(10000):
        name = names.get_full_name()
        adress = str(random.randint(1, 99)) + " " + names.get_full_name() + "75000, Paris"
        month = random.randint(1,12)
        if month <10 : month = "0" + str(month)
        else: month = str(month)
        day= random.randint(1,28)
        if day<10 : day= "0" + str(day)
        else: day= str(day)
        dateOfBirth = str(random.randint(1900, 2022))+ "/" + month +"/"+ day
        userData = "name:" + name + " - adress:" + adress + "-dateOfBirth:" + dateOfBirth + "- -" + str(random.randint(0,10)) + "-"+ str(random.randint(0,100))
        saintPaul .addUser(userData)
    print("selling ticket to random users")
    for _ in range(100000):
        userIndex = random.randint(0, len(saintPaul.userList)-1)
        saintPaul.sellTicket(saintPaul.userList[userIndex])
    print("generating the csv")
    df = pd.DataFrame.from_dict(saintPaul.getMetroData()).transpose()
    print("writing the csv file")
    df.to_csv("business.csv", sep=",", index=False)
    print("Today the station" + saintPaul.name + " earned : " + str(saintPaul.getDaylyRecet())+ " €")
    print("adding extra column to the dataframe, will be written in a new csv")
    df = df.assign(moneySpent= df["nbTicketBought"]* df["ticketPrice"])
    df=df.assign(stationRecette= df.moneySpent.sum())
    df.to_csv("completed business.fcsv", sep=",", index=False)

if __name__ == '__main__':
    main()