# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 15:05:27 2021

@author: robin
"""

import pip

if int(pip.__version__.split('.')[0])>9:
    from pip._internal import main
else:
    from pip import main
def install(package):
    main(['install', package])

install('BeautifulSoup4')


from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class Message(object):
    def __init__(self, message):
        self.date = datetime.strptime(message.find('div', class_="_3-94 _2lem").text, '%d %b %Y, %H:%M')
        self.sender = message.find('div', class_="_3-96 _2pio _2lek _2lel").text
        self.text = message.find('div', class_="_3-96 _2let").text
        self.words = self.get_word_list()
        self.reacts = self.count_reacts()
     
    
    def count_reacts(self):
        reacts = {}
        for react in '❤😆😮😢👍👎😍😠':
            reacts[react] = self.text.count(react)
        return reacts
    
    def get_word_list(self):
        wordstring = ''
        for char in self.text:
            if char in '❤😆😮😢👍👎😍😠':
                break
            if char in ' qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM':
                wordstring = wordstring + char.lower()
        wordlist = wordstring.split(' ')
        return wordlist
            
    def __str__(self):
        return str(self.date) + '\n' + self.sender + '\n' + self.text
    

class MessageSet(object):
    def __init__(self, messages):
        self.messages = messages
        self.senders = self.get_senders()
        self.years = self.get_years()
        # self.dict = self.get_message_dict()
    
    def get_senders(self):
        senders = []
        for message in self.messages:
            if not message.sender in senders:
                senders+=[message.sender]
        return senders
    
    def get_years(self):
        years = []
        for message in self.messages:
            #Senders
            if not message.date.year in years:
                years+=[message.date.year]
        years.reverse()
        return years


    def messages_by_sender(self, sender):
        """
        Takes a sender's name as a string
        Returns a set object of message objects sent by that sender
        """
        results = []
        for message in self.messages:
            if message.sender == sender:
                results+=[message]
        return MessageSet(results)    
    
    def messages_from_year(self, year):
        """
        Takes a year as an int
        Returns a set object of messages from that year
        """
        results = []
        for message in self.messages:
            if message.date.year == year:
                results += [message]
        return MessageSet(results)
    
    def messages_from_month(self, month):
        """
        Takes a month as an int (Jan = 1 etc.)
        Returns a set object of messages from that month
        """
        results = []
        for message in self.messages:
            if message.date.month == month:
                results+=[message]
        return MessageSet(results)
    
    def messages_with_word(self, word):
        """
        Takes a key word as a string
        Returns a set object of messages containing that word
        """
        results = []
        for message in self.messages:
            if word in message.words:
                results += [message]
        return MessageSet(results)    
    
    def search(self, sender = None, word = None, year = None, month = None):
        """        
        Returns a set object of messages meeting all search requirements
        """
        messageset = self
        if word != None:
            messageset = messageset.messages_with_word(word)
        if sender != None:
            messageset = messageset.messages_by_sender(sender)
        if month != None:
            messageset = messageset.messages_from_month(month)
        if year != None:
            messageset = messageset.messages_from_year(year)
        return messageset
    
    def count_word(self, word):
        """
        Takes a key word as a string
        Returns the total number of uses of that word in the messages
        """
        count = 0
        for message in self.messages:
            count += message.words.count(word)
        return count
    
    def count_word_per_sender(self, word):
        """
        Takes a key word as a string
        Returns the total number of uses of that word by each sender
        """
        results = { name : 0 for name in self.senders}
        for message in self.messages:
            if word in message.text:
                results[message.sender] += message.words.count(word)
        return results
    
    def count_messages_per_sender(self):
        """
        Returns a dict showing how many messages each participant has sent
        """
        results = {name : 0 for name in self.senders}
        for message in self.messages:
            results[message.sender] += 1
        return results
    
    def most_used_words(self, num_words=500):
        """
        Returns a dictionary of the top n words in the chat
        and how many times they were used
        """
        results = {}
        for message in self.messages:
            for word in message.words:
                if not word in results:
                    results[word]=1
                else:
                    results[word]+=1
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        return results[0:num_words]
                    
    def total_reacts(self):
        """
        Returns a dict of each react and how many times it is used 

        """
        totalreacts = {}
        for react in '❤😆😮😢👍👎😍😠':
            totalreacts[react] = sum([message.reacts[react] for message in self.messages])
        totalreacts['❤'] += totalreacts['😍']
        totalreacts.pop('😍')
        totalreacts['Total']=sum(totalreacts.values())
        return totalreacts    
    
    def get_react_dict(self):
        """
        Returns a dict of senders names and the reacts their messages got

        """
        results = {}
        for sender in self.senders:
            sent = self.messages_by_sender(sender)
            results[sender] = sent.total_reacts()
        return results
            
    def most_reacts(self):
        """
        Prints which sender received the most of each react, and how many times they received it
        """
        react_dict = self.get_react_dict()
        for react in ['❤','😆','😮','😢','👍','👎','😠','Total']:
            winner = ''
            most = 0
            for sender in react_dict.keys():
                if react_dict[sender][react] > most:
                    winner = sender
                    most = react_dict[sender][react]
            print(react, winner, most)                
            
    def avg_reacts_per_message(self):
        """
        Returns a dict of each react and how many times it is used on average per message

        """
        reacts = self.total_reacts()
        for react in reacts.keys():
            reacts[react]/=len(self.messages)
        return reacts
        
    def react_dict_per_message(self):
        """
        Returns a dict of senders names and the reacts they got on average per message

        """
        results = {}
        for sender in self.senders:
            sent = self.messages_by_sender(sender)     
            results[sender] = sent.avg_reacts_per_message()
        return results
    
    def most_reacts_per_message(self):
        """
        Prints which sender received the most of each react on average per message
        """
        react_dict = self.react_dict_per_message()
        for react in ['❤','😆','😮','😢','👍','👎','😠','Total']:
            winner = ''
            most = 0
            for sender in react_dict.keys():
                if react_dict[sender][react] > most:
                    winner = sender
                    most = react_dict[sender][react]
            print(react, winner, round(most,3))
        
    
class MessengerChat(MessageSet):
    def __init__(self, file_names):
        MessageSet.__init__(self, self.scrape_messages(file_names))
        self.messages, self.renamings, self.nicknamings, self.links, self.gamescores = self. parse_messages(self.messages)
        
    def parse_messages(self, messages):
        """
        Takes a list of message objects
        Returns list of unique sender names
        """
        nicknamings = []       
        renamings = []        
        links = []
        gamescores = []
        videochats = []
        adds = []
        emojisets = []
        pollvotes = []
        
        for message in messages:
            #pollvotes
            if 'voted for' in message.text and 'in the poll.' in message.text:
                pollvotes+=[message]
            #emojisets
            elif 'set the emoji to' in message.text:
                emojisets+=[message]
            #adds
            elif 'added' in message.text and 'to the group.' in message.text:
                adds+=[message]
            #vid chats
            elif 'video chat' in message.text:
                videochats+=[message]                
            #Renamings
            elif 'named the group' in message.text:
                renamings+=[message]
            #Nicknamings
            elif 'set the nickname for' in message.text or 'set your nickname to' in message.text:
                nicknamings+=[message]  
            #Links
            elif 'sent an attachment' in message.text or 'sent a link' in message.text:
                links+=[message]      
            # remove gamepoints
            else:
                for game in ['Snake.', 'Master Archer.', 'Kaburin!']:            
                    if game in message.text:
                        for phrase in ['leader board', 'set a new personal best of', 'points', 'is now in first place', 'challenged you']:
                            if phrase in message.text:
                                gamescores += [message]
                                break 
        nonmessages = pollvotes+emojisets+adds+videochats+renamings+nicknamings+ links + gamescores
        for message in nonmessages:
            messages.remove(message)
            
        return (messages, renamings, nicknamings, links, gamescores)
    
    
    
            
    def scrape_messages(self, file_names):
        """
        Takes a html file of a messenger conversation.
        returns a list of message objects.
        """
        message_list = []
        for file in file_names:
            with open(file, encoding='utf-8') as html_file:
                soup = BeautifulSoup(html_file, 'lxml')            
            message_boxes = soup.find_all('div', class_="pam _3-95 _2pi0 _2lej uiBoxWhite noborder")
            message_boxes.pop(0)
            for message in message_boxes:
                message_list += [Message(message)]
        return message_list







def PlotMessagesPerSender(messageset):
        """
        takes list of message objects
        plots a bar graph showing how many messages each person sent
        """
        messages_per_sender = messageset.count_messages_per_sender()
        
        messages_per_sender = sorted(messages_per_sender.items(), key=lambda x: x[1], reverse=True)
        
        names = [key for key,value in messages_per_sender]
        counts = [value for key,value in messages_per_sender]
        
        plt.bar(names, counts, color='g', width = 0.5, align='center')
        plt.title('Messages sent per person')
        plt.rc('xtick', labelsize='smaller') 
        plt.xticks(rotation=90)
        plt.show()
        
    
def plot_word_usage_by_year(messageset, word, years=None):
    if years == None:
        years = messageset.years
    count = []
    for year in years:
        messages = messageset.messages_from_year(year)
        count += [messages.count_word(word)/len(messages.messages)*1000]
    plt.plot(years, count, 'r-')
    plt.title('\''+word+'\'')
    plt.ylabel('Uses per 1000 messages')
    plt.xlabel('Year')
    plt.show
    

def plot_messages_per_month(messageset, years= None, style = 'r-'):
    if years == None:
        years = messageset.years
    monthticks = []
    count = []
    for year in years: 
        yearmessages = messageset.messages_from_year(year)
        for month in range(1,13):
            messages = yearmessages.messages_from_month(month)
            monthticks += [datetime(year = year, month = month, day = 1)]
            count += [len(messages.messages)]
    while count[0] == 0:
        count.pop(0)
        monthticks.pop(0)
    while count[-1] == 0:
        count.pop(-1)
        monthticks.pop(-1)
        
      # make rolling average   
    avgs = []
    for i in range(len(count)):
        if i==0:
            avgs += [(count[i]+count[i+1])/2]
            
        elif i == len(count)-1:
            avgs += [(count[i]+count[i-1])/2]
        else:
            avgs += [(count[i]+count[i-1]+count[i+1])/3]
        
    fig, ax = plt.subplots()    
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.plot(monthticks, avgs, style)
    # plt.plot(monthticks, count, 'b-')
    plt.rc('xtick', labelsize='small')
    plt.title('Messages sent per month')
    plt.show    

#plot_messages_per_month(group_chat)


def plot_word_usage(messageset, word, years = None, style='r-'):
    if years == None:
        years = messageset.years
    monthticks = []
    count = []
    for year in years:
        yearmessages = messageset.messages_from_year(year)
        for month in range(1,13):
            messages = yearmessages.messages_from_month(month)
            monthticks += [datetime(year = year, month = month, day = 1)]
            try:
                count += [messages.count_word(word)/len(messages.messages)*1000]
            except:
                count += [0]
                
    while count[0] == 0:
        count.pop(0)
        monthticks.pop(0)
    while count[-1] == 0:
        count.pop(-1)
        monthticks.pop(-1)
                
     # make rolling average   
    avgs = []
    for i in range(len(count)):
        if i==0:
            avgs += [(count[i]+count[i+1])/2]
            
        elif i == len(count)-1:
            avgs += [(count[i]+count[i-1])/2]
        else:
            avgs += [(count[i]+count[i-1]+count[i+1])/3]
       
    fig, ax = plt.subplots()
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_locator(mdates.YearLocator())    
    plt.plot(monthticks, avgs, style)
    #plt.plot(monthticks, count, 'r-')
    plt.title("\'"+word+"\'")
    plt.ylabel('Uses per 1000 messages')
    plt.show

#group_chat.most_reacts()
#group_chat.most_reacts_per_message()

#plot_word_usage(group_chat, 'beans', style = '#FFA500')
# plot_word_usage(group_chat, 'zoom', years=range(2015, 2018))
# plot_word_usage(group_chat, 'big')
# plot_word_usage(group_chat, 'nye')
# plot_word_usage(group_chat, 'great')
# plot_word_usage(group_chat, 'brek')
# plot_word_usage(group_chat, 'keen', years= range(2015,2020), style='b-')
