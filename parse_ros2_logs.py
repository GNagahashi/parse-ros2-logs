#!/usr/bin/python3

from csv import writer
from os.path import (
    abspath,
    isfile,
)
from pyparsing import (
    ParseException,
    Word,
    Suppress,
    OneOrMore,
    alphanums,
)


class InputFileNotExistError(Exception):
    """パース処理したいログファイルがないことを表す例外"""

    def __str__(self):
        return 'InputFileNotExistError: Input file not exist'


class ParseRos2Logs():
    """ROS2のログメッセージを処理するためのクラス

    ログメッセージをトークンごとに切り分けてカンマ区切りで出力する

    Attributes:
        input_files (list[str]): パース処理したいログファイル
        output_file (str): パース処理したログメッセージを保存するファイル
    """

    # ログメッセージのパターン
    __pattern = (
        OneOrMore(
            Suppress('[')
            + Word(alphanums + '!"#$%&\'()*+,-./:;<=>?@\\^_`{|}~')
            + Suppress(']')
        )
        + Suppress(':')
        + Word(alphanums + ' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
    )

    def __init__(self, input_files, output_file):
        self.__input_files = list()
        try:
            for i in input_files:
                if isfile(abspath(i)):
                    self.__input_files.append(i)
                else:
                    print(f'"{i}" is not file (ignore this file).')
            if self.__input_files == []:
                raise InputFileNotExistError
        except InputFileNotExistError as e:
            exit(e)
        self.__output_file = output_file

    def __read_line(self):
        """ファイルを1行単位で読み取るジェネレータ"""
        for file in self.__input_files:
            if not isfile(abspath(file)):
                continue
            with open(file, mode = 'r', encoding = 'utf-8') as f:
                for line in f:
                    yield line.strip()

    def __parse(self):
        """ファイルから読み取ったログメッセージをパース処理するジェネレータ"""
        for target in self.__read_line():
            try:
                result = self.__pattern.parse_string(target)
            except ParseException:
                yield None
            else:
                yield result

    def parse_logs(self):
        """パース処理したログメッセージをファイルに書き込むメソッド"""
        try:
            with open(self.__output_file, mode = 'x', encoding = 'utf-8', newline = '') as f:
                handler = writer(f)
                for i in self.__parse():
                    if not i == None:
                        handler.writerow(i)
        except FileExistsError as e:
            exit(e)


def main():
    # example
    log_data = ParseRos2Logs(
        input_files = ['sample/demo_log_01.txt', 'sample/demo_log_02.txt'],
        output_file = 'output.csv',
    )
    log_data.parse_logs()


if __name__ == '__main__':
    main()