import random
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image
from wordcloud import WordCloud

from notion_nlp.parameter.config import PathParams, ResourceParams, VisualParams
from notion_nlp.parameter.utils import unzip_webfile

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent.parent
EXEC_DIR = Path.cwd()


def word_cloud_plot(
    word_cloud_dataframe: pd.DataFrame,
    task_name: str = "word_cloud",
    save_path: str = (EXEC_DIR / PathParams.wordcloud.value).as_posix(),
    background_path: Optional[str] = None,  # todo 背景图片可以加到task的参数中，每个task的词云图背景不一样，也可以随机
    font_path: Optional[str] = None,
    width: int = 800,  # todo 词云图的宽、高也放到task参数中（作为可选项）
    height: int = 450,
    colormap: str = "viridis",  # todo 词云图的颜色也是可选项，可以指定自己想要的颜色
    font_show: str = "chinese.stzhongs.ttf",
):
    """绘制词云图

    Args:
        word_cloud_dataframe (pd.DataFrame): _description_
        task_name (str, optional): _description_. Defaults to "word_cloud".
        save_path (str, optional): _description_. Defaults to (EXEC_DIR / PathParams.wordcloud.value").as_posix().
        background_path (Optional[str], optional): _description_. Defaults to None.
        font_path (Optional[str], optional): _description_. Defaults to None.
        width (int, optional): _description_. Defaults to 800.
        height (int, optional): _description_. Defaults to 450.
        colormap (str, optional): _description_. Defaults to "viridis".

    Raises:
        ValueError: _description_
        ValueError: _description_
    """
    data_dict = dict(word_cloud_dataframe)

    # 设置词云图的基本参数
    # colormap: 全部生成/随机1张/指定类型
    colormap_list = [colormap]
    colormap_types = VisualParams.colormap_types()
    colormap_commands = ["random", "all"]  # 这个是用于代码逻辑的，就不抽象到参数类了
    if colormap == "random":
        colormap_list = [random.choice(colormap_types)]
    elif colormap == "all":
        colormap_list = colormap_types
    elif colormap not in colormap_types:
        raise ValueError(f"{colormap} is not in {colormap_types + colormap_commands}")

    # 判断是否需要下载字体
    font_path = font_path or (EXEC_DIR / PathParams.fonts.value / font_show).as_posix()
    if not Path(font_path).exists():
        Path(font_path).parent.mkdir(exist_ok=True, parents=True)
        unzip_webfile(ResourceParams.font_url.value, Path(font_path).parent.as_posix())
    # 如果不是字体文件，抛出异常
    elif not (font_path.lower().endswith(".ttf") or font_path.lower().endswith(".otf")):
        raise ValueError(f"{font_path} is not a ttf or otf file")

    for colormap in colormap_list:
        wc = WordCloud(
            width=width,
            height=height,
            colormap=colormap,
            font_path=font_path,
            prefer_horizontal=1,
            mode="RGBA" if background_path else "RGB",
            background_color="rgba(255, 255, 255, 0)" if background_path else "white",
        )
        wc.generate_from_frequencies(data_dict)

        outfile_path = Path(save_path) / task_name / f"colormap_{colormap}.png"
        outfile_path.parent.mkdir(exist_ok=True, parents=True)
        wc.to_file(outfile_path)

        if background_path:
            # Image process
            image = Image.fromarray(wc.to_array())
            background = Image.open(background_path).convert("RGBA")
            background = background.resize(image.size)
            new_image = Image.alpha_composite(background, image)
            # Save
            bkg_name, _ = Path(background_path).name.split(".", 1)
            name, ext = outfile_path.name.split(".", 1)
            new_name = f"{name}.{bkg_name}.{ext}"
            new_path = outfile_path.parent / new_name
            new_image.save(new_path)
            # fig = plt.imshow(new_image)
            # fig.axes.get_xaxis().set_visible(False)
            # fig.axes.get_yaxis().set_visible(False)
            # plt.savefig(outfile_path,
            #             bbox_inches='tight',
            #             pad_inches=0,
            #             format='png',
            #             dpi=300)
