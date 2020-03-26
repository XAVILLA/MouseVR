"""Script that will load the most recent file in the BehavioralData/data folder on the lab Computer,
 and then assuming the file is the output of a training run, will print out the number of licks both before and after the reward was delivered.

 9/16/19 (Gavin) - Changed program so that on top of counting licks, it would also output the time each lick took place (for those before the reward was delivered.)



"""

#Imports
import os
import time



def custom_max(directory,x):
    """
    Takes in the name of a file, returns the time the file was last modified (Citation needed).
    """
    time = -1
    if os.path.getsize(os.path.join(directory,x)) != 0 and 'Notes' not in x:
        time = os.path.getctime(os.path.join(directory,x))
    return time


def count_stops(text):
    """
    A method which takes in the text extracted from a test file, and returns the number of times the mouse stopped.
    (Not sure if it works or what the tolerance is. - Gavin)
    """
    b = text.splitlines()[1]
    stops = 0
    distances = [i.split(",")[2] for i in b[1:] if len(i.split(",")) > 2]
    for i in range(len(distances) - 1):
        if distances[i] == distances[i + 1]:
            stops += 1
    return stops

def displayTime(start_time,timestamp):
    """
    Parameters:
    start_time (str or int): the first timestamp of the function
    time_stamp (str or int): the timestamp of the event in question

    Return:
    (str) - Returns the amount of time that passed in seconds as a string, formated to two decimal places.

    9/16/19 (Gavin) - Creation of Method
    """
    return "{0:.2f}".format((int(timestamp)-int(start_time))/1000000)


def count_lick_times(text,found):
    """
    Parameters:
    text (str): the text extracted from one of the file outputs of the vr machine.

    Will print out the time in seconds of each lick that took place before the reward was delivered, as well as the reward time.

    9/16/19 (Gavin) - Creation of Method
    """
    text = text[:found]
    start_time = text.splitlines()[0].split(',')[0]
    lick_count = 0;
    for line in text.splitlines():
        data = line.split(',')
        if(data[1] == 'LK'):
            lick_count +=1
            print("Lick: " + str(lick_count) + " at time: " + displayTime(start_time,data[0]) + " seconds")
    print("Reward Delivery Time: " + displayTime(start_time,int(text.splitlines()[len(text.splitlines())-1].split(',')[0])) + ' seconds')

def main():
    try:
        #Directory where the file is held
        directory = os.path.join(os.path.expanduser("~"),'Desktop','BehavioralData','data')

        #Prints out the directory, then finds the most recent file in the directory and extracts text from it.
        print(directory)
        most_recent = max(os.listdir(directory), key=lambda x: custom_max(directory,x))
        text = open(os.path.join(directory,most_recent)).read()
        count_one = 0
        count_two = 0

        #If a reward was delivered, sets 'found' to the point in the text file where the reward was delivered. Otherwise sets found to the end of the text.
        found = len(text)
        try:
            found = text.index("TTT")
        except:
            pass

        #Displays all the information extracted back to the user
        print(most_recent[:most_recent.index(".txt")])
        #Not sure this method currently works so it is being commented out for now.
        #print(str(count_stops(text[:found])) + " stops")
        print(str(text[:found].count("LK")) + " licks before reward")
        print(str(text[found:].count("LK")) + " licks after reward")
        print("\n")
        count_lick_times(text,found)
        input("Press any ENTER to continue")
    except Exception as e:
        print(e)
        input("Press Enter to quit")

if __name__ == "__main__":
    main()
