# 日志模块
import logging
from pathlib import Path

import pandas as pd
from functional import seq
from functional.pipeline import Sequence

from notion_rich_text_analysis.notion_db_text import NotionDBText

PROJECT_ROOT_DIR = "notion_rich_text_analysis"


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

        self.task_name = task_name
        self.task_describe = task_describe
        self.database_id = database_id
        self.extra_data = extra_data

    def run(
        self,
        stopwords: set = set(),
        output_dir: Path = Path(f"{PROJECT_ROOT_DIR}/results"),
        top_n: int = 5,
        split_pkg: str = "pkuseg",
    ):
        """运行任务

        Args:
            stopwords (set, optional): 停用词集合. Defaults to set().
            output_dir (pathlib.Path, optional): 输出目录. Defaults to Path('./').
            top_n (int, optional): 输出得分排名前n个词. Defaults to 5.
        """
        self.handling_sentences(stopwords, split_pkg)
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
        return word in stopwords or word.isdigit() or not word.strip()

    @staticmethod
    def check_sentence_available(text: str):
        """检查句子是否符合要求

        Args:
            text (str): 输出的文本

        Returns:
            Bool: 是否符合要求
        """
        # 不要'#'开头的，因为可能是作为标签输入的，也可以用来控制一些分版本的重复内容
        if text.startswith("#"):
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
            import jieba

            return jieba.lcut(sentence, HMM=True)

        def _pkuseg(sentence):
            import pkuseg

            return pkuseg.pkuseg().cut(sentence)

        pkg_map = dict(jieba=_jieba, pkuseg=_pkuseg)

        if pkg not in pkg_map:
            raise ValueError(f"No module named {pkg}")
        return pkg_map[pkg](sentence)

    def handling_sentences(self, stopwords: set, split_pkg: str):
        """处理所有文本：分词、清洗、建立映射

        Args:
            stopwords (set): 停用词集合

        Raises:
            ValueError: 检查文本是否为空
        """
        logging.info("handling sentences....")
        # 检查数据库中获取的富文本是否为空
        if not self.total_texts:
            logging.error(
                f"该任务未获取到符合条件的文本，请检查筛选条件。database ID: {self.database_id}; extra data: {self.extra_data}"
            )
            raise ValueError("empty rich texts.")

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
        if not self.sequence:
            logging.error(
                f"该任务未获取到符合条件的文本，请检查停用词。database ID: {self.database_id}; extra data: {self.extra_data}"
            )
            raise ValueError("empty rich texts.")

        # 获取词表
        self.unique_words = self.sequence.map(lambda sent: set(sent)).reduce(
            lambda x, y: x.union(y)
        )

        # 检查词表是否为空
        if not self.unique_words:
            logging.error(
                f"词表为空，请检查筛选条件及停用词。database ID: {self.database_id}; extra data: {self.extra_data}"
            )
            raise ValueError("empty unique words")

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
        output_dir: Path = Path(f"{PROJECT_ROOT_DIR}/results"),
        top_n=5,
    ):
        """输出分析结果

        Args:
            task_name (str): 任务名
            task_describe (str): 任务描述
            output_dir (Path, optional): 输出路径. Defaults to Path('./').
            top_n (int, optional): 需要输出得分前n的词. Defaults to 5.
        """
        import re

        self.directory = Path(output_dir)
        self.directory.mkdir(exist_ok=True)

        # 按不同统计方法逆序输出所有词的tf-idf
        result_type = "tf_idf"
        task_name_clean = re.sub(r"\s", "_", task_name.strip())
        result_suffix = f"{task_name_clean}.{result_type}.analysis_result"
        result_attr_list = ["by_mean_drop_maxmin", "by_max", "by_sum"]
        for attr in result_attr_list:
            func = getattr(self, attr, self.empty_func)(self.tf_idf_dataframe)
            if func.empty:
                continue
            func.to_csv(self.directory / f"{result_suffix}.{attr}.csv")
        self.top_freq(
            self.tf_idf_dataframe,
            f"{result_suffix}.top{top_n}_word_with_sentences.md",
            task_describe,
            top_n,
        )

        logging.info(f"{self.task_name} result files have been saved to {output_dir}.")

    def top_freq(self, df: pd.DataFrame, file_name: str, task_describe: str, top_n: int):
        """检查高频词

        Args:
            df (pd.DataFrame): 词表与tf-idf的关联dataframe
            file_name (str): 输出的文件名
            task_describe (str): 任务描述
            top_n (int): 需要输出得分前n的词
        """
        with open(self.directory / file_name, "w") as f:
            f.write("# " + task_describe + "\n\n")
            for word in df.sum(axis=0).sort_values(ascending=False).head(top_n).index:
                f.write("## " + word + "\n\n")
                f.write(
                    "\n\n".join(
                        [
                            sent.replace("\n", " ").replace(word, f"**{word}**")
                            for sent in self.word2sents[word]
                        ]
                    )
                    + "\n\n"
                )

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
