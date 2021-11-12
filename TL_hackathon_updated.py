#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#https://api.liquipedia.net/documentation/api/v2/placement
#https://api.liquipedia.net/documentation/api/v2/openapi
#


# In[340]:


import requests
import json
import numpy as np
import inflect

import speech_recognition as sr
from win32com.client import Dispatch


# In[48]:


#header file
headers={'authorization':'Apikey pjyDDxPiOVhDIDJiTbKZfzUdd9IdYIxWEbksNOS3XulObkODfd9iUdZ9kNXQYxuqDppInKX7eJ712e46V1lUAyIoOkQCJjI4IfemKGj7ftDV7sD2CAsBjjMJ2qlEzJB7'}


# In[293]:


#explore speech recognition 
#help got from https://realpython.com/python-speech-recognition/ 
#need pyaudio as well to capture mic input 

def getplayername():

    import speech_recognition as sr
    from win32com.client import Dispatch

    #using default google api
    r=sr.Recognizer()

    #set up microphone class 
    mic=sr.Microphone(); #set up mic input 

    #==========let user search a name==================  

    speak = Dispatch("SAPI.SpVoice").Speak
    speak("say a player name by saying, search player name. For example, search Faker")
    speak("my creator is canadian, and he trained me by making me watch Jacob two two, so please repeat yourself twice. Thank you, thank you")

    #make sure I heard correctly

    heard=0;
    while heard==0:
        with mic as source:
            #r.adjust_for_ambient_noise(source, duration=0.5)
            speak("I'm listening now")
            r.adjust_for_ambient_noise(source, duration=2.5);
            audio = r.listen(source)

        #do voice recognition to get player name
        try:
            player_name=r.recognize_google(audio);
        except:
            print("Try saying their name again");

        #check if i got it right
        print(player_name)
        speak("did you say, "+player_name)

        with mic as source:
            speak("say yes or no")
            r.adjust_for_ambient_noise(source, duration=2);
            audio = r.listen(source)
            correctornot=r.recognize_google(audio);
            if correctornot=="yes":
                heard=1
            else:
                speak("try searching again")
                
    return player_name

#clean up output  
exit=0;

while exit==0:

    a=getplayername()
    asplit=a.split(); 
    playername=asplit[1:len(asplit)] #isolate player name 


    # In[294]:


    #check if player name is accurate by matching to list of lol players 
    found=0;
    while found==0:

        speak = Dispatch("SAPI.SpVoice").Speak
        speak("finding your player in the database")


        api_url_players="https://api.liquipedia.net/api/v2/player"; #api link
        formcond='[[pagename::>'+playername[0][0].upper()+']]';

        #which params to use for filtering 
        params= {'wiki':'leagueoflegends',
                 'conditions':formcond,
                 'query':'pagename',
                 'order':"pagename ASC",
                 'limit':'200'};

        #get info from api
        response = requests.get(api_url_players,headers=headers,params=params)
        response.json()

        #how to extract data from json object 
        a_list=response.json()['result'] #outputs a list which has a dictionary in it 
        #a['pagename'] #sometimes there is a dictionary in a dictionary

        #make list of player names 
        playernames=[];
        for player in a_list: 
            playernames.append(player['pagename']);

            if player['pagename'].lower()==playername[0]:
                print("player matched");
                speak("we have found a player");
                foundplayer=player['pagename'];
                found=1;
        if found==0: 
            print("player not found");
            speak("we could not find your player,please try again");
            a=getplayername()
            asplit=a.split(); 
            playername=asplit[1:len(asplit)] #isolate player name 


    # In[295]:


    #at this point we should have a player name under var foundplayer

    formcond='[[pagename::'+foundplayer+']]';
    params= {'wiki':'leagueoflegends',
             'conditions':formcond};

    #get info from api
    response = requests.get(api_url_players,headers=headers,params=params)
    response.json()

    #how to extract data from json object 
    playerinfo=response.json()["result"][0]#outputs a list which has a dictionary in it 


    # In[300]:


    #speaking about general player info
    playertag=playerinfo["pagename"]      #in game name 
    name=playerinfo["name"]               #actual name 
    role=playerinfo["extradata"]['role']  #in game role 
    typeofinvolv=playerinfo["type"]       #player or coach or supp staff
    region=playerinfo["region"]           #region of birth
    birthdate=playerinfo["birthdate"]     #birthdate 
    team=playerinfo["team"]               #team name 
    sigchamp=playerinfo["extradata"]["signature"] #signature chamption 
    earnings=str(playerinfo["earnings"]) #total earnings 
    activeornot=playerinfo["status"] #player status 

    intro= name + ", born on " + birthdate + "  is also known as " + playertag +" in league of legends." 
    speak(intro)

    if role=="Streamer":
        speak("they are a streamer.")
    else: 
        speak("They are a " + role + " player.") 

    intro2="They are from "+ region
    speak(intro2)

    if len(team)>0: 
        speak("They now play for " + team);
    else: 
        speak("I do not know which team they have or are currently playing for.")

    if len(sigchamp)>0:
        speak("Their signature champion is"+ sigchamp);
    else: 
        speak("They do not have a signature champion")


    if len(earnings)>0:
        intro4="it is approximated that they have made " + earnings +" dollars in tournament winnings.";
        speak(intro4);
    else:
        speak("They have not made an money from tourament winnings apparently.")


    if activeornot=="Active":
        speak("they are still an active player.")
    else: 
        speak("they are no longer playing professionally.")




    # In[302]:


    #===================================talk about tournament placements===============================================
    #find every tournament that a player has gone too and find their standings 
    api_url_placement="https://api.liquipedia.net/api/v2/placement"; #api link

    #get all tournaments and placements of a player 
    condition1="[[players_p1::"+foundplayer+"]]"
    condition2="[[players_p2::"+foundplayer+"]]"
    condition3="[[players_p3::"+foundplayer+"]]"
    condition4="[[players_p4::"+foundplayer+"]]"
    condition5="[[players_p5::"+foundplayer+"]]"
    conditiondate="[[date::>1999]]"

    #theres some random data in 1970 in south wales :S 
    finalcond="("+condition1+" OR "+condition2+" OR "+condition3+" OR "+condition4+" OR "+condition5+") AND ("+conditiondate+")";


    #which params to use for filtering 
    params= {'wiki':'leagueoflegends',
             'conditions':finalcond,
            'query':'tournament,placement,date',
            'sort':'date ASC'} #sort isnt working 

    #get info from api
    response = requests.get(api_url_placement,headers=headers,params=params)
    #response.json()

    #how to extract data from json object 
    allresults=response.json()['result'] #outputs a list which has a dictionary in it 
    allresults[0]


    t_name=[];
    t_place=[];
    t_date=[]; 

    for tourn in allresults:
        #get each tourn and make it into a list of tournament name, and result 
        t_name.append(tourn['tournament']);
        t_place.append(tourn['placement']);
        t_date.append(tourn['date']);

    #take avg placement if placement is a range 
    ii=0; 
    for place in t_place:

        if len(place)>=3:
            place=place.split();
            place=place[0];
            place=place.split("-",1);

            val1=int(place[0]);
            val2=int(place[1]);
            t_place[ii]=(val1+val2)/2;

        if len(place)==1:
            t_place[ii]=int(place[0]);

        if len(place)==0:
            t_place[ii]='0';

        ii=ii+1;   


    #tournament data of player 
    t_data=np.array([t_name,t_place,t_date]); #combine into one np array 
    t_data=t_data[:,t_data[2,:].argsort()]; #sorted data by tournament date [ASC]


    # In[346]:


    #speak tournament standings 
    p=inflect.engine();

    if len(t_name)>0:
        speak("they have placed in numerous tournaments. here are the results.")
        speak("note that range of standings will be averaged.")
        for ii in range(len(t_name)):
            eventname=t_name[ii];
            avgplacement=t_place[ii];
            avgplacement_speak=p.ordinal(avgplacement); 
            eventdate=t_date[ii].split()[0]; 

            if int(avgplacement)==0:
                speak("they played at " + eventname + ", on "+ eventdate + " and placed last")
            else:   
                speak("they played at " + eventname + ", on "+ eventdate + " and placed " + avgplacement_speak)

    if len(t_name)==0:
        speak("they have not played in any tournaments")


    speak("that is all I know about"+playertag)

    #check if they want to exit or search for another player 
    speak(". if you would like to exit, say exit. Or else if you would like to search another player, say search");

     #do voice recognition to see if they want to search again

    r=sr.Recognizer()
    mic=sr.Microphone(); #set up mic input 
    heard1=0;
    while heard1==0:

        try:
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=2.5);
                audio = r.listen(source)
                exitorsearch=r.recognize_google(audio);
        except:
            print("please state your option again");

        #check if i got it right
        print(exitorsearch)
        speak("did you say, "+exitorsearch)

        with mic as source:
            speak("say yes or no")
            r.adjust_for_ambient_noise(source, duration=2.5);
            audio = r.listen(source)
            correctornot=r.recognize_google(audio);
            if correctornot=="yes":
                heard1=1;
                if exitorsearch=="exit":
                    exit=1; 
                    speak("I will exit now.")
                    #break
                if exitorsearch=="search":
                    speak("okay, lets search again")
                    exit=0; 
            if correctornot=="no":
                heard1=0; 

