from pathlib import Path
from PIL import Image
from engine.presenter import generate_master_presenter


def test_master_presenter_generated_portrait_and_chroma_green(tmp_path):
    path=Path(generate_master_presenter(tmp_path/"master.png"))
    assert path.exists()
    with Image.open(path) as im:
        assert im.size==(1080,1920)
        assert im.getpixel((0,0))==(0,255,0)
