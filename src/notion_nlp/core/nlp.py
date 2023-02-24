import logging
import os
import random
import re
from itertools import chain
from pathlib import Path
from typing import List, Optional

import jieba
import pandas as pd
from functional import seq
from functional.pipeline import Sequence
from PIL import Image
from tabulate import tabulate
from wordcloud import WordCloud

from notion_nlp.core.api import NotionDBText
from notion_nlp.parameter.config import (
    CleanTextParams,
    PathParams,
    ResourceParams,
    TextAnalysisParams,
)
from notion_nlp.parameter.error import NLPError
from notion_nlp.parameter.utils import unzip_webfile

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent.parent
EXEC_DIR = Path.cwd()


class NotionTextAnalysis(NotionDBText):
    """分析notion富文本信息"""

    def __init__(
        self,
        header: dict,
        task_name: str,
        task_describe: str,
        database_id: str,
        extra_data: dict,
    ):
        """初始化

        Args:
            header (dict): header信息
            task_name (str): 任务名
            task_describe (str): 任务描述
            database_id (str): 数据库ID
            extra_data (dict): 筛选排序的附加信息
        """
        super().__init__(header, database_id, extra_data)
        logging.info(f"{task_name} start, {task_describe}")
        self.read()
        logging.info(f"Unsupported types: {self.unsupported_types}")

        jieba.set_dictionary(
            EXEC_DIR
            / PathParams.jieba.value
            / os.path.basename(ResourceParams.jieba_dict_url())
        )
        jieba.initialize()

        self.task_name = task_name
        self.task_describe = task_describe
        self.database_id = database_id
        self.extra_data = extra_data

    def run(
        self,
        stopwords: set = set(),
        output_dir: Path = EXEC_DIR,
        top_n: int = 5,
        split_pkg: str = "jieba",
    ):
        """运行任务

        Args:
            stopwords (set, optional): 停用词集合. Defaults to set().
            output_dir (pathlib.Path, optional): 输出目录. Defaults to Path('./').
            top_n (int, optional): 输出得分排名前n个词. Defaults to 5.
            split_pkg (str, optional): 分词包. Defaults to "jieba".
        """
        # 把page中的段落分句
        self.total_texts = [
            list(chain.from_iterable([split_paragraphs(text) for text in page_texts]))
            for page_texts in self.total_texts
        ]
        self.handling_sentences(stopwords, split_pkg)

        # 输出多种NLP技术的分析结果
        self.tf_idf_dataframe = self.tf_idf(self.sequence)
        self.output(self.task_name, self.task_describe, output_dir, top_n)

    @staticmethod
    def check_stopwords(word: str, stopwords: set):
        """检查词语是否在停用词列表内

        Args:
            word (str): 待检查的词
            stopwords (set): 停用词集合

        Returns:
            Bool: 词语是否在停用词列表内
        """
        word = word.strip().lower()
        return word in stopwords or word.isdigit() or not word

    @staticmethod
    def check_sentence_available(text: str):
        """检查句子是否符合要求

        Args:
            text (str): 输出的文本

        Returns:
            Bool: 是否符合要求
        """
        # 不要'#'开头的，因为可能是作为标签输入的，也可以用来控制一些分版本的重复内容
        for head in CleanTextParams.discard_startswith():
            if text.startswith(head):
                return False
        # 一个正常的句子的字数在中文和英文中都有很大的差异，以下是两种语言中句子的平均字数：
        # 中文：一个正常的句子通常包含12 - 20个汉字，但是也可能更长。在写作中，句子的长度可以根据需要进行调整，但一般不会超过30个汉字。
        # 英文：一个正常的句子通常包含10 - 20个单词，但是也可能更长。在写作中，句子的长度可以根据需要进行调整，但一般不会超过30个单词。
        # 需要注意的是，这只是一个平均值，实际上句子的长度可以根据需要进行调整，取决于句子的复杂性、写作风格以及句子所要表达的内容等因素。
        if len(text) < CleanTextParams.min_sentence_length():
            return False
        if len(text) > CleanTextParams.max_sentence_length():
            return False
        return True

    @staticmethod
    def split_sentence(sentence: str, pkg: str):
        """分词

        Args:
            sentence (str): 句子
            pkg (str): 分词所用的包
        """

        def _jieba(sentence):
            return jieba.lcut(sentence, HMM=True)

        pkg_map = dict(jieba=_jieba)

        if pkg not in pkg_map:
            raise NLPError(f"No module named {pkg}")
        return pkg_map[pkg](sentence)

    def handling_sentences(self, stopwords: set, split_pkg: str):
        """处理所有文本：分词、清洗、建立映射

        Args:
            stopwords (set): 停用词集合

        Raises:
            NLPError: 检查文本是否为空
        """
        logging.info("handling sentences....")
        # 检查数据库中获取的富文本是否为空
        if not self.total_texts:
            logging.error(
                f"该任务未获取到符合条件的文本，请检查筛选条件。database ID: {self.database_id}; extra data: {self.extra_data}"
            )
            raise NLPError("empty rich texts.")

        # 剔除无效句子
        text_list = [
            text
            for item in self.total_texts
            for text in item
            if self.check_sentence_available(text)
        ]
        # 分词
        logging.info(f"Use {split_pkg} to split sentences")
        split_text_list = [self.split_sentence(text, pkg=split_pkg) for text in text_list]

        # 剔除停用词
        self.sequence = seq(split_text_list).map(
            lambda sent: [
                word for word in sent if not self.check_stopwords(word, stopwords)
            ]
        )
        # 检查序列是否为空
        if not any(self.sequence):
            logging.error(
                f"该任务未获取到符合条件的文本，请检查停用词。database ID: {self.database_id}; extra data: {self.extra_data}"
            )
            raise NLPError("empty rich texts.")

        # 获取词表
        self.unique_words = self.sequence.map(lambda sent: set(sent)).reduce(
            lambda x, y: x.union(y)
        )

        # 检查词表是否为空
        if not self.unique_words:
            logging.error(
                f"词表为空，请检查筛选条件及停用词。database ID: {self.database_id}; extra data: {self.extra_data}"
            )
            raise NLPError("empty unique words")
        logging.info(f"unique words: {len(self.unique_words)}")

        # 词 --> 句子 查询字典
        self.word2sents = self._word2sent(text_list, self.unique_words)

    @staticmethod
    def _word2sent(text_list: list, unique_words: set):
        """获取 词 --> 句子 查询字典

        Args:
            text_list (list): 文本列表
            unique_words (set): 词表

        Returns:
            dict: 词 --> 句子 查询字典
        """
        word2sents = {word.lower(): set() for word in unique_words}

        for text in text_list:
            for word in unique_words:
                if word in text:
                    word2sents[word.lower()].add(text)
        return word2sents

    @staticmethod
    def tf_idf(sequence: Sequence):
        """使用标准tf-idf工具来分析

        Args:
            sequence (Sequence): pyfunctional库的sequence对象

        Returns:
            DataFrame: 词表与tf-idf的关联dataframe
        """
        logging.info("calculating tf-idf...")
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(sequence.map(lambda x: " ".join(x)).to_list())
        feature_names = vectorizer.get_feature_names_out()
        denselist = vectors.todense().tolist()
        df = pd.DataFrame(denselist, columns=feature_names)
        return df

    @staticmethod
    def empty_func(*args, **kwargs):
        """空函数，返回一个空dataframe"""
        return pd.DataFrame()

    def output(
        self,
        task_name: str,
        task_describe: str,
        output_dir: Path = EXEC_DIR,
        top_n=5,
    ):
        """输出tf-idf分析结果

        Args:
            task_name (str): 任务名
            task_describe (str): 任务描述
            output_dir (Path, optional): 输出路径. Defaults to Path('./').
            top_n (int, optional): 需要输出得分前n的词. Defaults to 5.
        """
        import re

        # 总输出目录
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)

        # 按不同统计方法逆序输出所有词的tf-idf

        # 任务名的空格转为下划线
        task_name_clean = re.sub(r"\s", "_", task_name.strip())

        # tfidf方法的输出路径
        tfidf_output_dir = output_dir / PathParams.tfidf_analysis.value
        tfidf_output_dir.mkdir(exist_ok=True, parents=True)

        # 文件后缀
        result_attr_list = ["by_mean_drop_maxmin", "by_max", "by_sum"]
        for attr in result_attr_list:
            func = getattr(self, attr, self.empty_func)(self.tf_idf_dataframe)
            if func.empty:
                continue
            func.to_csv(
                tfidf_output_dir / f"{task_name_clean}.{attr}.csv", header=["score"]
            )

        # 输出高分词
        self.top_freq(
            df=self.tf_idf_dataframe,
            file_name=f"{task_name_clean}.top_{top_n}.md",
            output_dir=tfidf_output_dir,
            task_describe=task_describe,
            top_n=top_n,
        )
        logging.info(
            f"{self.task_name} result markdown have been saved to {output_dir.absolute()}"
        )

        # 词云图
        wordcloud_save_path = output_dir / PathParams.wordcloud.value
        word_cloud_plot(
            self.by_mean_drop_maxmin(self.tf_idf_dataframe),
            task_name=task_name_clean,
            save_path=wordcloud_save_path,
            colormap="all",
        )
        logging.info(f"word cloud plot saved to {wordcloud_save_path.absolute()}")

    def top_freq(
        self, df: pd.DataFrame, file_name: str, output_dir, task_describe: str, top_n: int
    ):
        """检查高频词

        Args:
            df (pd.DataFrame): 词表与tf-idf的关联dataframe
            file_name (str): 输出的文件名
            task_describe (str): 任务描述
            top_n (int): 需要输出得分前n的词
        """
        # todo top_freq是通用方法，要从类中拆出来
        top_n_words = self.by_mean_drop_maxmin(df).head(top_n)
        print(
            tabulate(
                pd.DataFrame(top_n_words),
                headers=["word", "score"],
                tablefmt="rounded_grid",
            )
        )
        with open(output_dir / file_name, "w", encoding="utf-8") as f:
            f.write("# " + task_describe + "\n\n")
            f.write("## Top " + str(top_n) + " words\n\n")
            f.write("|Word|Score|\n|---|---|\n")
            top_words = [f"|{word}|{score}|" for word, score in top_n_words.items()]
            f.write("\n".join(top_words) + "\n\n")
            for word in top_n_words.index:
                f.write("## " + word + "\n\n")
                f.write(
                    "\n\n".join(
                        [
                            "- " + sent.replace("\n", " ").replace(word, f"**{word}**")
                            for sent in self.word2sents[word]
                        ]
                    )
                )
                f.write("\n\n")

    @staticmethod
    def by_mean_drop_maxmin(df: pd.DataFrame):
        """去除最大最小值，计算均值，逆序

        Args:
            df (DataFrame): 词表与tf-idf的关联dataframe

        Returns:
            _type_: _description_
        """
        # 剔除最大最小值，求均值
        df_drop_maxmin = df.copy()
        for col in df.columns:
            df_drop_maxmin[col] = df[col][df[col].between(df[col].min(), df[col].max())]
            df_drop_maxmin[col].dropna(inplace=True)
        return df_drop_maxmin.mean().sort_values(ascending=False)

    @staticmethod
    def by_max(df: pd.DataFrame):
        """按词在不同文档中最大值逆序

        Args:
            df (pd.DataFrame): 词表与tf-idf的关联dataframe

        Returns:
            Series: 词语得分逆序
        """
        # 最大值
        return df.max(axis=0).sort_values(ascending=False)

    @staticmethod
    def by_sum(df: pd.DataFrame):
        """按词在不同文档中的分数和逆序

        Args:
            df (pd.DataFrame): 词表与tf-idf的关联dataframe

        Returns:
            Series: 词语得分逆序
        """
        # 求和
        return df.sum(axis=0).sort_values(ascending=False)


# def computeTF(wordDict, bagOfWords):
#     tfDict = {}
#     bagOfWordsCount = len(bagOfWords)
#     for word, count in wordDict.items():
#         tfDict[word] = count / float(bagOfWordsCount)
#     return tfDict


# def computeIDF(documents):
#     import math

#     N = len(documents)

#     idfDict = dict.fromkeys(documents[0].keys(), 0)
#     for document in documents:
#         for word, val in document.items():
#             if val > 0:
#                 idfDict[word] += 1

#     for word, val in idfDict.items():
#         idfDict[word] = math.log(N / float(val))
#     return idfDict


def word_cloud_plot(
    word_cloud_dataframe: pd.DataFrame,
    task_name: str = "word_cloud",
    save_path: str = (EXEC_DIR / PathParams.wordcloud.value).as_posix(),
    background_path: Optional[str] = None,  # todo 背景图片可以加到task的参数中，每个task的词云图背景不一样，也可以随机
    font_path: Optional[str] = None,
    width: int = 800,  # todo 词云图的宽、高也放到task参数中（作为可选项）
    height: int = 450,
    colormap: str = "viridis",  # todo 词云图的颜色也是可选项，可以指定自己想要的颜色
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
    # colormap: 全部生成/随机1张/指定类型  # todo 将该功能扩展出去
    colormap_list = [colormap]
    colormap_commands = ["random", "all"]  # 这个是用于代码逻辑的，就不抽象到参数类了
    if colormap == "random":
        colormap_list = [random.choice(TextAnalysisParams.colormap_types())]
    elif colormap == "all":
        colormap_list = TextAnalysisParams.colormap_types()
    elif colormap not in TextAnalysisParams.colormap_types():
        raise ValueError(
            f"{colormap} is not in {TextAnalysisParams.colormap_types() + colormap_commands}"
        )

    # 判断是否需要下载字体
    font_path = (
        font_path
        or (EXEC_DIR / PathParams.fonts.value / TextAnalysisParams.font_show()).as_posix()
    )
    if not Path(font_path).exists():
        Path(font_path).parent.mkdir(exist_ok=True, parents=True)
        unzip_webfile(TextAnalysisParams.font_url(), Path(font_path).parent)
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

        outfile_path = Path(save_path) / f"{task_name}/colormap_{colormap}.png"
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


# 把段落按句号、分号、问号等分隔符切分为句子
def split_paragraphs(paragraph: str) -> List[str]:
    """把段落按句号、分号、问号等分隔符切分为句子

    Args:
        paragraphs (List[str]): 段落列表

    Returns:
        List[List[str]]: 切分后的句子列表
    """
    # todo 改用成熟的句子切分工具，如 Stanford CoreNLP、NLTK 和 SpaCy 等，它们都能够处理多种语言中的句子切分问题。

    # 匹配中英文标点符号后面可能跟着的零个或多个空白字符，再匹配一个非空白字符。其中，中英文标点符号包括句号（。）、分号（；）、问号（？）、感叹号（！）和英文标点符号（.、;、?、!）
    pattern = r"(?<=[。；？！\.;?!])\s*(?=[^\s。；？！\.;?!])"
    sentences = re.split(pattern, paragraph)
    return sentences
