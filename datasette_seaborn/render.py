import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import io
import sys


def render_records(records, method, kwargs):
    mpl.rcParams.update(mpl.rcParamsDefault)
    sns.set_theme()
    plt.close("all")
    # Start a new figure
    plt.figure(figsize=(8, 5))

    df = pd.DataFrame.from_records(records)
    method_fn = getattr(sns, method)

    figure = method_fn(data=df, **kwargs)
    png = io.BytesIO()
    if not hasattr(figure, "savefig"):
        figure = figure.get_figure()
    figure.savefig(png, format="png")
    if hasattr(figure, "clf"):
        figure.clf()
    else:
        figure.fig.clf()
    sys.stdout.buffer.write(png.getvalue())
