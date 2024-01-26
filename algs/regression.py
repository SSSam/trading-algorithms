import matplotlib.pyplot as plt
import csv, sys

class RegressionLine:
    def __init__(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values
        self.line_price = sum(y_values) / len(y_values)  # Average price of the regression line
        self.size = len(x_values)  # will always be 1 on init
        self.support = False
        self.resistance = False
    
    def add_point(self, x, y):
        self.x_values.append(x)
        self.y_values.append(y)
        self.line_price = sum(self.y_values) / len(self.y_values)  # update average price
        self.size += 1

def plot_regression_lines(regression_lines, significant_values, main_lines):
    (support_line, resis_line)= main_lines
    plt.figure(figsize=(12, 8))
    
    for y, x in significant_values:
        plt.scatter(x,y, color='red')
        plt.annotate(f'({x}, {y})', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        
    for line in regression_lines:
        if line.support:
            plt.hlines(y=line.line_price, xmin=min(line.x_values), xmax=max(line.x_values), colors='green', linestyles='dashed')
            plt.text(max(line.x_values), line.line_price, f' {line.line_price:.2f}', verticalalignment='center', fontsize=8, color='green')
        elif line.resistance:
            plt.hlines(y=line.line_price, xmin=min(line.x_values), xmax=max(line.x_values), colors='red', linestyles='dashed')
            plt.text(max(line.x_values), line.line_price, f' {line.line_price:.2f}', verticalalignment='center', fontsize=8, color='red')
        else:
            plt.hlines(y=line.line_price, xmin=min(line.x_values), xmax=max(line.x_values), colors='blue', linestyles='dashed')
            plt.text(max(line.x_values), line.line_price, f' {line.line_price:.2f}', verticalalignment='center', fontsize=8, color='purple')
    try:
        if support_line.line_price or resis_line.line_price:
            # Main Support Line
            plt.hlines(y=support_line.line_price, xmin=min(support_line.x_values), xmax=max(support_line.x_values), colors='green', linestyles='solid')
            plt.text(max(support_line.x_values), support_line.line_price, f' {support_line.line_price:.2f} (Main Support)', verticalalignment='center', fontsize=8, color='green')

            # Main Resistance Line
            plt.hlines(y=resis_line.line_price, xmin=min(resis_line.x_values), xmax=max(resis_line.x_values), colors='red', linestyles='solid')
            plt.text(max(resis_line.x_values), resis_line.line_price, f' {resis_line.line_price:.2f} (Main Resistance)', verticalalignment='center', fontsize=8, color='red')

            pass
    except AttributeError as e:
        print(f"Support/Resistance Line Not found: {e}")
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


def import_csv(file_path):
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        return [(float(row[0]), int(row[1])) for row in reader]


class WyckoffAnalysis:
    def __init__(self, regression_lines, intervals_to_switch=5):
        self.regression_lines = regression_lines
        self.intervals_to_switch = intervals_to_switch

    def basic_categorization(self, current_price):
        for line in self.regression_lines:
            if current_price > line.line_price:
                line.support = True
                line.resistance = False
            else:
                line.resistance = True
                line.support = False
        main_support_line= self.find_main_support(current_price)
        main_resistance_line= self.find_main_resistance(current_price)
        return (main_support_line, main_resistance_line)

    def find_main_support(self, current_price):
        support_lines = [line for line in self.regression_lines if line.support]
        if support_lines:
            main_support = min(support_lines, key=lambda x: abs(x.line_price - current_price))
            return main_support

    def find_main_resistance(self, current_price):
        resistance_lines = [line for line in self.regression_lines if line.resistance]
        if resistance_lines:
            main_resistance = min(resistance_lines, key=lambda x: abs(x.line_price - current_price))
            return main_resistance

    def categorization_switch(self, current_price):
            above_resistance_count = 0
            below_support_count = 0

            for line in self.regression_lines:
                if line.resistance and current_price > line.line_price:
                    above_resistance_count += 1
                    below_support_count = 0  # Reset below_support_count if above resistance
                elif line.support and current_price < line.line_price:
                    below_support_count += 1
                    above_resistance_count = 0  # Reset above_resistance_count if below support

                if above_resistance_count >= self.intervals_to_switch:
                    line.resistance = False
                    line.support = True
                    above_resistance_count = 0
                    print("Resistance line ==> Support")

                if below_support_count >= self.intervals_to_switch:
                    line.support = False
                    line.resistance = True
                    below_support_count = 0
                    print("Support line ==> Resistance")


#  USAGE
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python regression.py <csv_file_path>")
        sys.exit(1)
    csv_file_path = sys.argv[1]
# csv_file_path = 'test2.csv'  # replace it with other input file path for testing
    
significant_values = import_csv(csv_file_path)
print(significant_values) # significant_values = [(price, time (seconds))]

regression_lines = establish_regression_lines(significant_values)

# Create WyckoffAnalysis instance
wyckoff_analysis = WyckoffAnalysis(regression_lines)

# Set the current market price
current_price = 98.0  # Replace with whatever the current price is, can be automated

# Basic Categorization
for line in regression_lines:
    print(f"Line Price: {line.line_price}, Points: {list(zip(line.y_values, line.x_values))} Line Size: {line.size}")

# Categorization Switch
prices= [price for price, _ in significant_values]

for current_price in prices:
    (support_line, resis_line)= wyckoff_analysis.basic_categorization(current_price)
    wyckoff_analysis.categorization_switch(current_price)

try:
    if support_line.line_price or resis_line.line_price:
        print(f"Main Support Price: {support_line.line_price}, Points: {list(zip(support_line.y_values, support_line.x_values))} Line Size: {support_line.size}")
        print(f"Main Resistance Price: {resis_line.line_price}, Points: {list(zip(resis_line.y_values, resis_line.x_values))} Line Size: {resis_line.size}")
        pass
except AttributeError as e:
    print(f"Support/Resistance Line Not found: {e}")
plot_regression_lines(regression_lines, significant_values, (support_line, resis_line))