import matplotlib.pyplot as plt

class RegressionLine:
    def __init__(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values
        self.line_price = sum(y_values) / len(y_values)  # Average price of the regression line
        self.size = len(x_values)  # will always be 1 on init
    
    def add_point(self, x, y):
        self.x_values.append(x)
        self.y_values.append(y)
        self.line_price = sum(self.y_values) / len(self.y_values)  # update average price
        self.size += 1

def plot_regression_lines(regression_lines, significant_values):
    plt.figure(figsize=(12, 8))
    
    for y, x in significant_values:
        plt.scatter(x,y, color='red')
        plt.annotate(f'({x}, {y})', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        
    for line in regression_lines:
            plt.hlines(y=line.line_price, xmin=min(line.x_values), xmax=max(line.x_values), colors='blue', linestyles='dashed')
            plt.text(max(line.x_values), line.line_price, f' {line.line_price:.2f}', verticalalignment='center', fontsize=8, color='purple')
    
    plt.title('Regression Lines with Significant Points')
    plt.xlabel('Time (Seconds)')
    plt.ylabel('Price (Dollars)')
    plt.show()


def establish_regression_lines(significant_values, p_percentage=0.0015):
    if len(significant_values) < 3:
        return []  # Not enough data

    # store regression lines in a list
    regression_lines = []

    # go thru the significant values
    for price, time in significant_values:
        min_diff = float('inf')
        min_line = None # we store the line with the minimum difference here

        for line in regression_lines:
             # calculat difference between the current price and the line's price
            if abs(price - line.line_price) <= p_percentage * line.line_price:
                diff = abs(price - line.line_price)

                if diff < min_diff:  # Update min_diff and min_line if this line is the closest one so far
                    min_diff = diff
                    min_line = line

        # add the value to the regresson line if a suitible line is found
        if min_line:
            min_line.add_point(time, price)

        else:
            # make a new line if the value doesn't fit with another line
             regression_lines.append(RegressionLine([time], [price])) # create a new regression line of 1 size.

    regression_lines = [line for line in regression_lines if line.size >= 3] # filter out any lines that are smaller than 3 points
            
    return regression_lines

#  USAGE

significant_values = [
    # (price, time (seconds))
    (98.5, 596),
    (99.9, 600),
    (97.3, 652),
    (99.34, 680),
    (98.9, 684),
    (99.3, 696),
    (98.24, 712),
    (98.75, 730),
    (98.3, 744),
    (98.7, 766),
    (97.25, 784),
    (98.95, 814),
    (97.3, 915),
    (97.95, 930),
    (97.35, 940),
    (98.35, 960),
]

regression_lines = establish_regression_lines(significant_values)

# print values
for line in regression_lines:
    print(f"Line Price: {line.line_price}, Points: {list(zip(line.y_values, line.x_values))} Line Size: {line.size}")

#visualize, debug use only
plot_regression_lines(regression_lines, significant_values)



