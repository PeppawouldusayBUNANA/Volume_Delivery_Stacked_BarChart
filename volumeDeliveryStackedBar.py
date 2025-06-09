import pandas
from tkinter import Tk, Label, Entry, Button, Text, END
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('dark_background')

# === Search Window ===
def search_stock():
    symbol = entry.get().strip().upper()
    volume = volume_dict.get(symbol)
    delivery_perc = delivery_dict.get(symbol)
    
    result_box.delete("1.0", END)

    if volume is not None and delivery_perc is not None:
        delivery_volume = volume * (delivery_perc / 100)
        result = f"Symbol: {symbol}\nToday's Volume: {volume}\nDelivery %: {delivery_perc:.2f}%\nDelivery Volume: {delivery_volume:.2f}"
    else:
        result = f"Symbol '{symbol}' not found in both datasets."
    
    result_box.insert(END, result)

# Tkinter GUI
root = Tk()
root.title("Stock Volume & Delivery Lookup")

Label(root, text="Enter Stock Symbol:").pack(pady=5)
entry = Entry(root)
entry.pack()

Button(root, text="Search", command=search_stock).pack(pady=5)

result_box = Text(root, height=6, width=50)
result_box.pack(pady=10)



# File selection
bhavcopy_file = askopenfilename(title="Select the Bhavcopy file", filetypes=[("CSV files", "*.csv")])
volume_file = askopenfilename(title="Select the Volume file", filetypes=[("CSV files", "*.csv")])
if not bhavcopy_file or not volume_file:
    print("No file selected. Exiting...")
    exit()

# Load Data
bhavcopy_df = pandas.read_csv(bhavcopy_file, skiprows=0)
bhavcopy_df.columns = bhavcopy_df.columns.str.strip()  # strip spaces from all column names
volume_df = pandas.read_csv(volume_file, skiprows=5)

bhavcopy_df = bhavcopy_df.loc[bhavcopy_df["SERIES"].str.strip() == "EQ"]
pandas.set_option('display.max_rows', None)

# Convert to numeric
bhavcopy_df["DELIV_PER"] = pandas.to_numeric(bhavcopy_df["DELIV_PER"], errors="coerce").fillna(0)
volume_df["Today's Volume"] = pandas.to_numeric(volume_df["Today's Volume"], errors="coerce").fillna(0)

symbols = volume_df["Symbol"].tolist()

volume_dict = {symbols[i]: volume_df.iloc[i]["Today's Volume"] for i in range(len(symbols))}
delivery_dict = {}
for i in range(len(bhavcopy_df)):
    symbol = bhavcopy_df.iloc[i]["SYMBOL"].strip()
    delivery_percentage = bhavcopy_df.iloc[i]["DELIV_PER"]
    delivery_dict[symbol] = delivery_percentage

common_symbols = sorted(set(volume_dict.keys()).intersection(set(delivery_dict.keys())))
delivery_volumes = [volume_dict[symbol] * (delivery_dict[symbol] / 100) for symbol in common_symbols]
remaining_volumes = [volume_dict[symbol] - delivery_volumes[i] for i, symbol in enumerate(common_symbols)]

# === Stacked Bar Chart ===
max_symbols_per_plot = 78

# === New plotting function: delivery % inside volume bar ===
def plot_delivery_inside_volume(symbols, volumes, delivery_percents, title):
    fig, ax = plt.subplots(figsize=(20, 10))
    indices = np.arange(len(symbols))

    # Plot total volume bars in blue
    ax.bar(indices, volumes, color='blue', label="Total Volume")

    # Plot delivery volume as red bars inside the blue bars
    delivery_heights = np.array(volumes) * (np.array(delivery_percents) / 100)
    ax.bar(indices, delivery_heights, color='red', label="Delivery Volume")
    ax.set_xlabel("Symbols")
    ax.set_ylabel("Volume")
    ax.set_title(title)
    ax.set_xticks(indices)
    ax.set_xticklabels(symbols, rotation=90)
    ax.legend()
    plt.tight_layout()
    plt.show()


# Prepare data for plotting
delivery_percents = [delivery_dict[symbol] for symbol in common_symbols]
volumes = [volume_dict[symbol] for symbol in common_symbols]

# Plot in parts if too many symbols
if len(common_symbols) > max_symbols_per_plot:
    for part in range(0, len(common_symbols), max_symbols_per_plot):
        part_symbols = common_symbols[part:part + max_symbols_per_plot]
        part_volumes = volumes[part:part + max_symbols_per_plot]
        part_delivery_perc = delivery_percents[part:part + max_symbols_per_plot]
        plot_delivery_inside_volume(
            part_symbols,
            part_volumes,
            part_delivery_perc,
            f"Volume and Delivery % (Part {part // max_symbols_per_plot + 1})"
        )
else:
    plot_delivery_inside_volume(common_symbols, volumes, delivery_percents, "Volume and Delivery %")

root.mainloop()
