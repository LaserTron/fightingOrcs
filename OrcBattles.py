#!/bin/python3

############
# Packages #
############
import random
import string
import pandas as pd
from datetime import date
today = lambda : date.today().isoformat()

#################
# Dice rolling  # 
#################

#dice
d2 = lambda :random.randint(1,2)
d6 = lambda :random.randint(1,6)
d8 = lambda :random.randint(1,8)
d20 = lambda :random.randint(1,20)
d = lambda n : random.randint(1,n)

def roll(dstring):
    "parses stuff like 4d4+3 and returns result of a roll"
    terms = dstring.split("+")
    res = []
    for t in terms:
        if "d" in t:
            dd=t.split("d")
            num=dd[0]
            if num=="":
                num=1
            else:
                num=int(num)
            sides=int(dd[1])
            subtotal = 0
            for i in range(num):
                subtotal+=random.randint(1,sides)
            res.append(subtotal)
        else:
            res.append(int(t))
    return sum(res)


#############################
# Orc convenience functions #
#############################

statbonus = lambda n : (n-10)//2

def get_random_string(length):
    "Outputs a random orc name"
    letters = 'gharkqsto'
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

#################
# The orc class #
#################

class Orc:
    """An orc, by default all stats are rolled. Otherwise rebuilds an orc
from a dictionary containing statistics."""
    def __init__(self,statDict=None):
        if statDict == None:
            self.name = get_random_string(12).title()
            self.team = "Orc College"
            self.str = d6()+d6()+d6()
            self.con = d6()+d6()+d6()
            self.dex = d6()+d6()+d6()
            self.hp_max = max(4,d8())+statbonus(self.con)
            self.level = 1
            self.xp = 0
            self.weapon_name = 'fists' 
            self.weapon_dmg = "d2"
            self.armour_name = 'nothing'
            self.armour_bonus=0
            self.armour_max_dex=10
            self.hp_current = self.hp_max
            self.salary = 1
            self.playing = 1
        else:
            self.name = statDict['name']
            self.team = statDict['team']
            self.str = int(statDict['str'])
            self.con = int(statDict['con'])
            self.dex = int(statDict['dex'])
            self.hp_max = int(statDict['hp_max'])
            self.level = int(statDict['level'])
            self.xp = int(statDict['xp'])
            self.weapon_name = statDict['weapon_name']
            self.weapon_dmg = statDict['weapon_dmg']
            self.armour_name = statDict['armour_name']
            self.armour_bonus= int(statDict['armour_bonus'])
            self.armour_max_dex= int(statDict['armour_max_dex'])
            self.hp_current = int(statDict['hp_current'])
            self.salary = int(statDict['salary'])
            self.playing = int(statDict['playing'])
            
        #Variables that get changed
        self.game_record = {
            "attack": [],
            "defense":[],
            "dmg_dealt":0,
            "dmg_received":0
        }
        self.initiative = 0
        if self.playing and self.hp_current >0:
            self.standing = True
        else:
            self.standing = False
        self.opponents = []
        

    def attack_mod(self):
        return self.level+statbonus(self.str)
    
    def dex_mod(self):
        return min(statbonus(self.dex),self.armour_max_dex)
    
    def attack_roll(self):
        dmg = max(roll(self.weapon_dmg)+statbonus(self.str),1)
        return [d(20)+self.attack_mod(),dmg]
    
    def resolve_hit(self,hit):
        "hit is a pair from attack roll"
        roll = hit[0]
        dmg = hit[1]
        armour_bonus=self.armour_bonus
        if roll < 10+self.dex_mod(): 
            result="dodges"
        elif roll < 10+self.dex_mod()+armour_bonus:
            result="blocks"
        else:
            self.hp_current = self.hp_current-dmg
            if self.hp_current <=0:
                result="falls"
                self.game_record['dmg_received']+=dmg
                self.fall()
            else:
                self.game_record['dmg_received']+=dmg
                result=" takes {0} damage".format(dmg)
        self.game_record['defense'].append(result)
        return result
            
    def attack_orc(self,target):
        attack_string = "{0} of team {1} attacks {2} of team {3}.".format(self.name,self.team,target.name,target.team)
        attack = self.attack_roll()
        effect = target.resolve_hit(attack)
        if effect == "falls":
            levup = self.xp_up(target.level)
            self.game_record['dmg_dealt']+=attack[1]
            self.game_record['attack']+=["hit"]
        elif effect=="dodges" or effect=="blocks":
            self.game_record['attack']+=["miss"]
        else:
            self.game_record['dmg_dealt']+=attack[1]
            self.game_record['attack']+=["hit"]            
        return attack_string+u"\n"+"{0} {1}.".format(target.name,effect) #debug
    
    
    def xp_up(self,n):
        levup = self.level*10
        self.xp = self.xp+n
        if self.xp >= levup:
            self.xp = self.xp-levup
            self.level_up()
        return "Level up"
    
    def level_up(self):
        hp_up = max(d(8)+statbonus(self.con),1)
        self.hp_current += hp_up
        self.hp_max += hp_up
        self.level += 1
        return "Level up, hp increased by {0}".format(hp_up)
    
    def add_weapon(self,wpn):
        self.weapon = wpn
        
    def add_armour(self,arm):
        self.armour = arm
        
    def reset_game_record(self):
        self.game_record = {
            "attack": [],
            "defense":[],
            "dmg_dealt":0,
            "dmg_received":0
        }
    def reset_equipment(self):
        self.weapon = ['fists',d2] #weapon name and attack dice as function
        self.armour = ['nothing',0,0] #armor name dex mod
        
    def stat_damage(self):
        stats = ["str","dex","con"]
        s = random.choice(stats)
        if s == "str": self.str = self.str -1
        if s == "dex": self.dex = self.dex -1
        else: self.con = self.con-1
        return "Permanent damage to {0}.".format(s)
    
    def add_opponent(self,opp):
        if not(opp in self.opponents):
            self.opponents.append(opp)
            opp.add_opponent(self)
            
    def remove_opponent(self,opp):
        if opp in self.opponents:
            self.opponents.remove(opp)
            opp.remove_opponent(self)
    
    def fall(self):
        """includes stat damage"""
        #remove self from lists
        self.standing = False
        for opp in self.opponents:
            opp.remove_opponent(self)
        #!!! fallen orc can still attack once
        #evaluate stat damage
        roll = d(20)
        if roll >self.con:
            self.stat_damage()
            
    def attack(self):
        try:
            target = random.choice(self.opponents)
            action = self.attack_orc(target)
            #print(action)#debug    
            return action
        except IndexError:
            return "No attack"
    
    def set_team(self,teamname):
        self.team = teamname
    
    def get_team(self):
        return self.team
    
    def rename(self,newname):
        self.name=newname
        
    def recover(self):
        recovery = max(1,statbonus(self.con))
        self.hp_current = min(self.hp_max,self.hp_current+recovery)
    
    def match_stats(self):
        attacks = self.game_record['attack']
        hits = [i for i in attacks if i =="hit"]
        defenses = self.game_record['defense']
        dodges = [i for i in defenses if i =="dodges"]
        blocks = [i for i in defenses if i =="blocks"]
        dealt = self.game_record['dmg_dealt']
        received = self.game_record['dmg_received']
        summary = {
            "team":self.team,
            "name": self.name,
            "attacks delivered": len(attacks),
            "hits": len(hits),
            "damage dealt": dealt,
            "attacks received": len(defenses),
            "dodges": len(dodges),
            "blocks":len(blocks),
            "damage received": received,
            "total xp":self.xp,
            "remaining hp":self.hp_current
        }
        return summary
    
    def opponent_count(self):
        return len(self.opponents)
    
    def get_opponent(self,lst):
        """goes through a list and returns an opponent with
        as few other opponents as possible"""
        nonteam = [x for x in lst if x.team != self.team]
        random.shuffle(nonteam)#<-- be fair!
        oppos = list(map(lambda i:i.opponent_count(),nonteam))
        self.add_opponent(nonteam[oppos.index(min(oppos))])

    def to_dict(self):
        statDict = {}
        statDict['name'] = self.name 
        statDict['team'] = self.team 
        statDict['str'] = self.str 
        statDict['con'] = self.con 
        statDict['dex'] = self.dex 
        statDict['hp_max'] = self.hp_max 
        statDict['level'] = self.level 
        statDict['xp'] = self.xp 
        statDict['weapon_name'] = self.weapon_name 
        statDict['weapon_dmg'] = self.weapon_dmg 
        statDict['armour_name'] = self.armour_name 
        statDict['armour_bonus'] = self.armour_bonus
        statDict['armour_max_dex'] = self.armour_max_dex
        statDict['hp_current'] = self.hp_current 
        statDict['salary'] = self.salary
        statDict['playing'] = self.playing
        for rec in self.game_record:
            statDict[rec] = self.game_record[rec]
        return statDict

########
# Team #
########
def generate_orc_roster(n):
    "Makes a dataframe with n orcs"
    L=map(lambda x:Orc(),range(n))
    DL = map(lambda x:x.to_dict(),L)
    return pd.DataFrame(DL)

class Team:
 
    def __init__(self,DF):
        """Takes an orc roster and makes a list"""
        diclist=DF.to_dict(orient="records")
        self.orcs = list(map(lambda x:Orc(statDict=x),diclist))
        self.name = self.orcs[0].team
    
    def set_name(self,name):
        self.name=name
        for o in self.orcs:
            o.set_team(name)
    
    def to_dataframe(self):
        diclist = list(map(lambda x:x.to_dict(),self.orcs))
        return pd.DataFrame(diclist)
    
    def match_stats(self):
        stats = list(map(lambda x:x.match_stats(),self.orcs))
        return pd.DataFrame(stats)
    
    def to_list(self):
        return self.orcs
        
    def recover(self):
        "Each orc recovers one day"
        for o in self.orcs:
            o.recover()
        
    def write_files(self):
        match = self.match_stats()
        stats = self.to_dataframe()
        fname1="{0} {1} data.csv".format(self.name,today())
        fname2="{0} {1} match summary.csv".format(self.name,today())
        match.to_csv(fname2)
        stats.to_csv(fname1)

def team_from_csv(fname):
    DF=pd.read_csv(fname)
    return Team(DF)
        
###########
# Battles #
###########

# Now some convenience functions for lists of orcs
def remove_fallen(lst):
    """removes fallen orcs from a list"""
    return [x for x in lst if x.standing]


def match_opponents(allorcs):
    #goes through a list of orcs, finds opponents for lonely orcs
    for i in allorcs:
        if i.opponent_count() ==0:
            i.get_opponent(allorcs)
            #print("New opponent!")
            
def still_standing(roster):
    roster = roster.to_list()
    standing = [o for o in roster if o.standing]
    return len(standing)

flatten = lambda l:[y for x in l for y in x] #<-makes a list of lists a list

def battle(teamlist):
    "takes a list of teams and resolves a battle"
    narration = ""
    allorcs = flatten(list(map(lambda x:x.to_list(),teamlist)))
    #!maybe shuffle allorcs
    finished = False
    allorcs = remove_fallen(allorcs)
    while not finished:
        for i in allorcs:
            narration+=i.attack()+"\n"
        allorcs = remove_fallen(allorcs)
        narration+="\n After this round...\n"
        for t in teamlist:
            line = "{0}: {1}\n".format(t.name,still_standing(t))
            narration+=line
        try:
            match_opponents(allorcs)
        except ValueError:
            narration+="The battle is OVER."
            finished = True
    #Wrap up and record
    fname = "The battle of {0}".format(today())
    f = open(fname,'w')
    f.write(narration)
    f.close()
    for i in teamlist:
        i.recover()
        i.write_files()
    return narration
