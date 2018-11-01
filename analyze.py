import sys
from datetime import datetime
from functools import reduce
import pandas as pd
from collections import Counter
import string
import difflib
import seaborn as sns
import matplotlib.pyplot as plt
import emoji


class Message:

    def __init__(self):
        self.sender = ''
        self.dateSent = datetime.now()
        self.text = []
        self.isContinuation = False
        self.IsError = False

    def getDateString(self, date: datetime) -> str:
        return date.strftime("%x")+" "+date.strftime("%X")

    def __str__(self) -> str:
        return "[%s] %s: %s" % (Message.getDateString(self, self.dateSent), self.sender, self.text)


TotalWordCount = 0
TotalMessageCount = 0
TotalAnalyzedLinesCount = 0
MessageList = []

PunctuationTable = str.maketrans(dict.fromkeys(string.punctuation+"’"))

# todo:
# count audio messages
# count image messages
# most used words per person


def sanitizeToMessage(line) -> list:
    endOfTimeStamp = line.find(']')
    if (endOfTimeStamp == -1):
        print("Fatal error: End of Timestamp not found in line:", line)
        raise ValueError(
            "Fatal error: End of Timestamp not found in line:" + line)

    endOfSender = line.find(':', endOfTimeStamp+1)
    if (endOfSender == -1):
        print("Fatal error: End of Sender not found in line:", line)
        raise ValueError(
            "Fatal error: End of Sender not found in line:" + line)

    return line[endOfSender+1:].lower().translate(PunctuationTable).split()


def getDateSent(line) -> datetime:
    endOfTimeStamp = line.find(']')
    if (endOfTimeStamp == -1):
        print("Fatal error: End of Timestamp not found in line:", line)
        quit()

    startOfTimeStamp = line.find('[')
    if (startOfTimeStamp == -1):
        print("Fatal error: Start of Timestamp not found in line:", line)
        quit()

    return datetime.strptime(line[startOfTimeStamp+1:endOfTimeStamp], "%m/%d/%y, %I:%M:%S %p")


def getSender(line) -> str:
    endOfTimeStamp = line.find(']')
    if (endOfTimeStamp == -1):
        print("Fatal error: End of Timestamp not found in line:", line)
        raise ValueError(
            "Fatal error: End of Timestamp not found in line:" + line)

    endOfSender = line.find(':', endOfTimeStamp+1)
    if (endOfSender == -1):
        print("Fatal error: End of Sender not found in line:", line)
        raise ValueError(
            "Fatal error: End of Sender not found in line:" + line)

    return line[endOfTimeStamp+2:endOfSender]


def getMessage(line, lastMessage) -> Message:
    global TotalWordCount

    message = Message()
    if line.find('[') != 0 and line.find('[') != 1:
        lastMessage.text = lastMessage.text + line.split()
        lastMessage.isContinuation = True
        return lastMessage

    else:
        try:
            message.isContinuation = False
            message.text = sanitizeToMessage(line)
            message.sender = getSender(line)
            message.dateSent = getDateSent(line)
        except ValueError:
            message.IsError = True
            return message

    return message


def read_data(filename):
    global TotalAnalyzedLinesCount
    global MessageList

    with open(filename) as f:
        lastMessage = Message()

        for line in f:
            lastMessage = getMessage(line, lastMessage)

            if not lastMessage.isContinuation and not lastMessage.IsError:
                MessageList.append(lastMessage)

            if (TotalAnalyzedLinesCount % 1000 == 0):
                print(TotalAnalyzedLinesCount)

            TotalAnalyzedLinesCount += 1


def parse(filename):
    fp = filename
    print('Looking for WhatsApp File: ', fp)
    read_data(fp)
    print('Message count: ', len(MessageList))
    return MessageList


def analyze(messageList):
    print("------------STATISTICS-------------\n\n\n")

    wordsDf = pd.DataFrame(data=list(map(lambda message: [message.sender, len(message.text)], messageList)), columns=[
                           "Sender", "Number of Words"]).groupby("Sender").agg({'Number of Words': 'sum'}).reset_index()

    messagesPerPersonDF = pd.DataFrame(data=list(map(lambda message: [message.sender, 1], messageList)), columns=[
        "Sender", "Number of Messages"]).groupby("Sender").agg({'Number of Messages': 'sum'}).reset_index()

    numberOfMessagesPerDayDF = pd.DataFrame(data=list(map(lambda message: [message.dateSent.date(), 1], messageList)), columns=[
        "Date Sent", "Number of Messages"]).groupby("Date Sent").agg({'Number of Messages': 'sum'}).reset_index()

    numberOfMessagesPerDayOfWeekDF = pd.DataFrame(data=list(map(lambda message: [message.sender, message.dateSent.date().strftime("%A"), 1], messageList)), columns=[
        "Sender", "Day of Week", "Number of Messages"]).groupby(["Day of Week", "Sender"]).agg({'Number of Messages': 'sum'}).reset_index()

    numberOfMessagesPerHourOfDayDF = pd.DataFrame(data=list(map(lambda message: [message.sender.split()[:1][0], message.dateSent.strftime("%H"), 1], messageList)), columns=[
        "Sender", "Hour of Day", "Number of Messages"]).groupby(["Hour of Day", "Sender"]).agg({'Number of Messages': 'sum'}).reset_index()

    # aggregate word count
    WordsDictionary = Counter()
    for message in messageList:
        for word in message.text:
            WordsDictionary[word] += 1

    with open(r"/mnt/d/Projects/ChatAnalysis/EnglishStopwords.txt") as f:
        for line in f:
            WordsDictionary[line.lower().rstrip(
            ).translate(PunctuationTable)] = 0
    wordCount = pd.DataFrame(
        data=WordsDictionary.most_common(15), columns=["Word", "Count"])

    # aggregate emoji count
    EmojiDictionary = Counter()
    for message in messageList:
        for word in message.text:
            if word in emoji.UNICODE_EMOJI:
                EmojiDictionary[word] += 1

    emojiCount = pd.DataFrame(
        data=EmojiDictionary.most_common(15), columns=["Emoji", "Count"])

    f = open(
        r"MessagesOverTime_days.txt", "w")
    f.write(numberOfMessagesPerDayDF.to_string())

    f = open(
        r"MessagesOverTime_weekdays.txt", "w")
    f.write(numberOfMessagesPerDayOfWeekDF.to_string())

    f = open(
        r"MessagesOverTime_hoursofday.txt", "w")
    f.write(numberOfMessagesPerHourOfDayDF.to_string())

    f = open(
        r"MessagesOverTime_hoursofday.txt", "w")
    f.write(numberOfMessagesPerHourOfDayDF.to_string())

    f = open(
        r"MostUsedWords.txt", "w")
    f.write(wordCount.to_string())

    f = open(
        r"MostUsedEmojis.txt", "w")
    f.write(emojiCount.to_string())

    # printing results
    # print("---Most Used Words---")
    # print(wordCount)
    # print("\n\n\n")

    # print("---Highest Volume Days---")
    # print(numberOfMessagesPerDayDF)
    # print("\n\n\n")

    # print("---Words Sent Per Person---")
    # print(wordsDf)
    # print("\n\n\n")

    # print("---Messages Sent By Weekday---")
    # print(numberOfMessagesPerDayOfWeekDF)
    # print("\n\n\n")

    # print("---Messages Sent By Hour of Day---")
    # print(numberOfMessagesPerHourOfDayDF)
    # print("\n\n\n")

    # sns.set(style="whitegrid")
    # #sns.set_color_codes("Spectral")
    # sns.barplot(x="Sender", y="Number of Messages", data=messagesPerPersonDF, palette='Spectral')

    # plt.show()
