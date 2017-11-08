import csv
from matplotlib import pyplot as plt
from datetime import datetime

filename = "C:\\Users\\Asymmetry\\Desktop\\death_valley_2014.csv"

with open(filename) as f:
    reader = csv.reader(f)
    header_row = next(reader)
    '''
    for index, column_header in enumerate(header_row):
        print(index, column_header)
    '''

    #get high temperatures from file
    dates, highs, lows = [], [], []
    for row in reader:
        try:
            date = datetime.strptime(row[0], "%Y-%m-%d")
            high = int(row[1])
            low = int(row[3])
            
        except ValueError:
            print(date,"missing data")
            
        else:        
            dates.append(date)
            highs.append(high)
            lows.append(low)
        
    '''
    print(highs)
    print(lows)
    print(dates)
    '''
    #plot data.
    fig = plt.figure(dpi = 128, figsize = (10, 6))
    plt.plot(dates, highs, c = "red")
    plt.plot(dates, lows, c = "blue")
    plt.fill_between(dates, highs, lows, facecolor = "blue", alpha = 0.1)

    plt.title("Daily high and low temperatures-2014", fontsize = 24)
    plt.xlabel("", fontsize = 16)
    fig.autofmt_xdate()
    
    plt.ylabel("Temperature(F)", fontsize = 16)
    plt.tick_params(axis = "both", which = "major", labelsize = 16)
    #plt.xticks(dates)

    plt.show()

    
