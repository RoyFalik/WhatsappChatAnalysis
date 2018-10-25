import sys
from datetime import datetime
from functools import reduce


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


def sanitizeToMessage(line) -> list:
    endOfTimeStamp = line.find(']')
    if (endOfTimeStamp == -1):
        print("Fatal error: End of Timestamp not found in line:", line)
        quit()

    endOfSender = line.find(':', endOfTimeStamp+1)
    if (endOfSender == -1):
        print("Fatal error: End of Sender not found in line:", line)
        quit()

    return line[endOfSender+1:].split()


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
        quit()

    endOfSender = line.find(':', endOfTimeStamp+1)
    if (endOfSender == -1):
        print("Fatal error: End of Sender not found in line:", line)
        quit()

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


print('Looking for WhatsApp File: ', str(sys.argv[1]))
read_data(sys.argv[1])
print('Message count: ', len(MessageList))

RoyMessage = list(filter(lambda message: message.sender == 'Roy', MessageList))
print(len(RoyMessage))

GonieMessage = list(filter(lambda message: message.sender == 'Gonie  Altman', MessageList))
print(len(GonieMessage))

RoyWordCount = list(map(lambda message: len(message.text), RoyMessage))
RoyWordCountTotal = reduce((lambda x, y: x + y), RoyWordCount)

GonieWordCount = list(map(lambda message: len(message.text), GonieMessage))
GonieWordCountTotal = reduce((lambda x, y: x + y), GonieWordCount)

print(RoyWordCountTotal)
print(GonieWordCountTotal)

