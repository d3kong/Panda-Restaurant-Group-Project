import os
import csv
import numpy as np
class Card_Number_Catcher:
    class Transaction:
        def __init__(self, store, id, card, day, minutes):
            self.store = store
            self.id = id
            self.card = card
            self.day = day
            self.minutes = minutes
        def __str__(self):
            return "Store: " + self.store + "," + " T ID: " + self.id + "," + " Card: " + self.card + " ||"
        def __repr__(self):
            return "Store: " + self.store + "," + " T ID: " + self.id + "," + " Card: " + self.card + " ||"            
        def __eq__(self, obj):
            if not isinstance(obj, type(self)): return NotImplemented
            return self.card == obj.card
        def __hash__(self):
            if self.card != None:
                return hash(self.card)
            else:
                return 0
        def has_null(self):
            return self.card == None or self.store == None or self.id == None
        
    IGNORE = ["1707", "1912", "1926", "1953", "1957", "2034", "2059",
            "2061", "2063", "2064", "2169", "2179", "2200", "2269", "524", "710", "827", "901",]
    store_num_index = 3
    acc_id_index = 1
    TRANSACTION_ID_INDEX = 5
    MAX_CARDS = 2
    MAX_MINUTE = 5
    card_collect = {}
    transaction_collect = {}
    day = ""


    def __init__(self, checkin, transaction):
        check_dir = os.fsencode(checkin)
        transaction_dir = os.fsencode(transaction)
        for transaction_day in os.listdir(transaction):
            
            with open("Transaction/" + os.fsdecode(transaction_day), 'r') as transaction_file:
                transaction_data = csv.reader(transaction_file, delimiter=',')
                all_data = []
                for row in transaction_data:
                    all_data.append(row)
            all_data.pop(0)
            for ln in all_data:
                self.transaction_filler(ln)
        suspect = "Suspects.txt"
        headers = "Account ID,# of cards on file\n"
        fWriter = open("Suspects.txt", 'w')
        i = 1
        for check_in_day in os.listdir(check_dir):
            with open("Checkin/" + os.fsdecode(check_in_day), 'r') as check_in_file:
                checkin_data = csv.reader(check_in_file, delimiter=',')
                all_data2 = []
                for row in checkin_data:
                    all_data2.append(row)
            self.day = all_data2[0][0].split(" ")[4]
            all_data2.pop(0)
            all_data2.pop(0)
            for ln in all_data2:
                self.check_in_filler(ln, i)
            i += 1

    def transaction_filler(self, ln):
        if len(ln[1]) < 18 or ln[1][0] != "P":
            return
        if ln[0] == "":
            temp = ln[1].split(" ")
            if len(temp[2]) > 4:
                ln[0] = temp[2][1:]
            else:
                ln[0] = temp[2]
        if ln[0] == 0 or len(ln[3]) > 6 or ln[3] == "0":
            return
        if ln[0] not in self.transaction_collect:
            self.transaction_collect[ln[0]] = {}
        if ln[3] not in self.transaction_collect[ln[0]]:
            self.transaction_collect[ln[0]][ln[3]] = ln[4]
    def check_in_filler(self, ln, i):
        if ln[2] == "OnlineCheckin" or ln[self.store_num_index] in self.IGNORE:
            return False
        if "" in ln:
            return False
        if ln[4].split(" ")[1] != self.day:
            return False
        if ln[self.store_num_index] not in self.transaction_collect and ln[self.store_num_index] not in self.IGNORE:
            txt = ln[self.store_num_index] + "\n"
            return False
        temp = None
        if ln[self.acc_id_index] in self.card_collect:
            if len(ln[self.TRANSACTION_ID_INDEX]) == 10:
                ln[self.TRANSACTION_ID_INDEX] = ln[self.TRANSACTION_ID_INDEX][4:]
            temp = self.Transaction(ln[self.store_num_index], ln[self.TRANSACTION_ID_INDEX], self.transaction_collect.get(ln[self.store_num_index]).get(ln[self.TRANSACTION_ID_INDEX]), i, self.minute_maker(ln[4]))
            self.card_collect[ln[self.acc_id_index]].add(temp)
        else:
            self.card_collect[ln[self.acc_id_index]] = set()
            if len(ln[self.TRANSACTION_ID_INDEX]) == 10:
                ln[self.TRANSACTION_ID_INDEX] = ln[self.TRANSACTION_ID_INDEX][4:]
            temp = self.Transaction(ln[self.store_num_index], ln[self.TRANSACTION_ID_INDEX], self.transaction_collect.get(ln[self.store_num_index]).get(ln[self.TRANSACTION_ID_INDEX]), i, self.minute_maker(ln[4]))
            self.card_collect[ln[self.acc_id_index]].add(temp)
        if temp.has_null():
            self.card_collect[ln[self.acc_id_index]].remove(temp)
        return len(self.card_collect[ln[self.acc_id_index]]) > self.MAX_CARDS
    def consecutive(self, history):
        temp = []
        for T in history:
            temp.append(T.minutes)
        temp.sort()
        counter = 0
        max = 1
        if len(history) > 4:
            max = len(history) - 2
        i = 1
        while i < len(temp):
            if temp[i] - temp[i - 1] <= self.MAX_MINUTE:
                counter += 1
            if counter >= max:
                return False
            i += 1
        return True

    def diff_days(self, history):
        temp = set()
        for T in history:
            temp.add(T.day)
        if len(temp) >= len(history):
            return False
        return True
    
    def print2(self):
        suspect = open("Suspects.txt", 'w')
        for acc_id in self.card_collect:
            if (len(self.card_collect[acc_id]) > self.MAX_CARDS) and self.consecutive(self.card_collect[acc_id]) and self.diff_days(self.card_collect[acc_id]):
                txt = acc_id + ": " + str(self.card_collect[acc_id]) + "\n"
                suspect.write(txt)  

    def minute_maker(self, date):
        temp = date.split(" ")
        time = temp[3].split(":")
        minutes = (int(time[0]) * 60) + int(time[1])
        if temp[4] == "PM":
            minutes += (12*60)
        return minutes