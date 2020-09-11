from datasette import hookimpl
from datasette.utils.asgi import Response
import seaborn as sns
import matplotlib as mpl
import pandas as pd
import io


def error(request, msg):
    return {"body": msg, "status_code": 500}


def render_seaborn(columns, rows, request):
    # _seaborn= provides the method
    # _seaborn_X provide the arguments
    method = request.args.get("_seaborn") or "NOMETHOD"
    if not hasattr(sns, method):
        return error(request, "_seaborn= is required")

    kwargs = {
        key.replace("_seaborn_", ""): request.args[key]
        for key in request.args
        if key.startswith("_seaborn_")
    }

    # Reset matplotlib
    mpl.rcParams.update(mpl.rcParamsDefault)
    sns.set_theme()

    df = pd.DataFrame.from_records(dict(row) for row in rows)
    method_fn = getattr(sns, method)

    figure = method_fn(data=df, **kwargs)
    png = io.BytesIO()
    if not hasattr(figure, "savefig"):
        figure = figure.get_figure()
    figure.savefig(png, format="png")
    return {"body": png.getvalue(), "content_type": "image/png"}


@hookimpl
def register_output_renderer(datasette):
    return {
        "extension": "seaborn",
        "render": render_seaborn,
    }
