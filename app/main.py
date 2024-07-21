"""Upload a bit.bin or a bin fw and flash the FPGA"""

from os import environ, unlink
from os.path import basename

from fastapi import BackgroundTasks, FastAPI, File, UploadFile, status
from fastapi.responses import HTMLResponse

from fpga_bit_to_bin import convert_bit_to_bin

FPGA = "/sys/class/fpga_manager/fpga0/firmware"

if "FPGA" in environ:
    FPGA = environ["FPGA"]


app = FastAPI()


async def upload_file(
    file: UploadFile,
):
    """upload_file"""
    ouput_path = f"/lib/firmware/{file.filename}"
    with open(ouput_path, "wb") as output:
        output.write(await file.read())
    return ouput_path


def flash_fpga(fw_bit_bin):
    """flash fpga"""
    with open(FPGA, "w") as fpga:
        fpga.writelines([basename(fw_bit_bin)])


@app.post("/flash_bit", status_code=status.HTTP_200_OK)
async def flash_bin(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """flash_bin"""
    path_bit = await upload_file(file)
    path_bin = f"{path_bit}.bin"
    convert_bit_to_bin(path_bit, path_bin, True)

    flash_fpga(path_bin)

    background_tasks.add_task(unlink, path_bit)
    background_tasks.add_task(unlink, path_bin)
    return {"message": "OK"}


@app.post("/flash_bit_bin_list/", status_code=status.HTTP_200_OK)
async def flash_bit_bin_list(
    background_tasks: BackgroundTasks, uploaded_files: list[UploadFile]
):
    """flash_bit_bin"""
    path_bin = await upload_file(uploaded_files[0])
    flash_fpga(path_bin)
    background_tasks.add_task(unlink, path_bin)
    return {"message": "OK"}


@app.post("/flash_bit_bin/", status_code=status.HTTP_200_OK)
async def flash_bit_bin(background_tasks: BackgroundTasks, uploaded_file: UploadFile):
    """flash_bit_bin"""
    path_bin = await upload_file(uploaded_file)
    flash_fpga(path_bin)
    background_tasks.add_task(unlink, path_bin)
    return {"message": "OK"}


HTML = """
<html>
<head>
    <title>Some Upload Form</title>
    <script src="https://unpkg.com/dropzone@5/dist/min/dropzone.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/dropzone@5/dist/min/dropzone.min.css" type="text/css" />
</head>
<body>
    <form action="/flash_bit_bin" class="dropzone" id="my-great-dropzone">
    </form>
    <script>
        Dropzone.options.myGreatDropzone = { // camelized version of the `id`
            paramName: "uploaded_files", // The name that will be used to transfer the file
            maxFiles: 1
        };
    </script>
</body>
</html>
"""


@app.get("/")
async def root():
    """form"""
    return HTMLResponse(HTML)
