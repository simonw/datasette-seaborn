from datasette import hookimpl
from datasette.utils.asgi import Response
import seaborn as sns
import pathlib
import asyncio, sys
import json

render_code = (pathlib.Path(__file__).parent / "render.py").read_text()

DEFAULT_TIME_LIMIT = 5.0


def error(request, msg):
    return {"body": msg, "status_code": 500}


async def render_seaborn(datasette, columns, rows, request):
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

    plugin_config = datasette.plugin_config("datasette-seaborn") or {}
    render_time_limit = plugin_config.get("render_time_limit") or DEFAULT_TIME_LIMIT

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-",
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )

    code = (
        render_code
        + "\n\n"
        + "null=None\n"
        + "true=True\n"
        + "false=False\n"
        + "render_records({records}, {method}, {kwargs})".format(
            records=json.dumps([dict(row) for row in rows]),
            method=json.dumps(method),
            kwargs=json.dumps(kwargs),
        )
    )

    image_bytes = []
    errors = []

    async def render_image():
        stdout_data, stderr_data = await proc.communicate(code.encode("utf-8"))
        if stdout_data:
            image_bytes.append(stdout_data)
        if stderr_data:
            errors.append(stdout_data)

    time_limit_hit = False
    # Run this with a time limit
    try:
        await asyncio.wait_for(render_image(), timeout=render_time_limit)
    except asyncio.TimeoutError:
        time_limit_hit = True
    try:
        proc.kill()
    except OSError:
        # Ignore 'no such process' error
        pass

    if time_limit_hit:
        return Response("Render took too long", status=500)
    elif errors:
        return Response("Errors occurred: {}".format(errors[0]), status=500)
    else:
        return Response(image_bytes[0], content_type="image/png")


@hookimpl
def register_output_renderer():
    return {
        "extension": "seaborn",
        "render": render_seaborn,
    }
