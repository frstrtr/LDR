import pandas as pd

def read_data(fname):
    # Read the CSV content
    df = pd.read_csv(fname)

    # Remove wrong magnitudes
    df = df.drop(df[df.mag < 0].index)
    magnitudes = df["mag"]

    # Get timestamp transformed to our timezone
    times = df["time"]#.apply(lambda x: transform_date(x, timezone))

    return times, magnitudes


if __name__ == "__main__":
    # options = argparse.ArgumentParser()
    # options.add_argument("-f", "--file", type=str, required=True)
    # args = options.parse_args()
    data = read_data('all_day.csv')
    x1,x2 = data
    for t in x1:
        print (t, type(t))


    print (type(data))
    print (data)