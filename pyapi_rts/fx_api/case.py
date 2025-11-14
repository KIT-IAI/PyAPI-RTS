import shutil
import zipfile
from pathlib import Path

from pyapi_rts.fx_api.protocols import AppProtocol, CaseProtocol


def change_case_file_canvas_size(path: Path, width: int, height: int):
    output_path = path.with_suffix('.rtfx.tmp')
    target_file = f'{path.stem}.dfx'
    with zipfile.ZipFile(path, 'r') as input_zip, zipfile.ZipFile(output_path, 'w') as output_zip:
        for item in input_zip.infolist():
            if item.filename == target_file:
                with input_zip.open(target_file) as file:
                    content = file.read().decode('utf-8')
                    modified_content = content.replace(
                        'SUBSYSTEM-CANVAS-SIZE:3000,2000',
                        f'SUBSYSTEM-CANVAS-SIZE:{width},{height}'
                    )
                output_zip.writestr(item, modified_content)
            else:
                output_zip.writestr(item, input_zip.read(item.filename))

    shutil.copyfile(output_path, path)
    output_path.unlink()


def create_new_case(file_path: Path, app: AppProtocol, width=8000, height=10000) -> CaseProtocol:
    file_path_string = str(file_path.absolute())
    file_path.unlink(missing_ok=True)

    case = app.new_case()
    case.save(file_path_string)
    case.close()

    change_case_file_canvas_size(file_path, width, height)

    case = app.open_case(file_path_string)
    return case
