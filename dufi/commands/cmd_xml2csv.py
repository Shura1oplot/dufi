# [SublimeLinter @python:3]

import argparse

import tkinter as tk

from .base import Command, InvalidCommandArgs
from ..utils import echo


TEXT = """
Dufi позволяет сконвертировать практически любой XML файл в набор плоских таблиц. \
При этом под каждый тэг будет создана отдельная таблица. \
Все записи таблицах будут содержать ссылку на родителя. \
Такой подход позволяет SQL запросом собрать любую плоскую таблицу на основе иерархического XML файла.

Чтобы сконвертировать один или несколько однотипных XML файлов в плоский табличный формат, нужно:
 1. В разделе "Other...", который слева, выбрать команду "xml2db-schema".
 2. Выбрать XML файлы кнопкой "Add..." или перетащив их в окно программы.
 3. В поле "--out-schema" выбрать файл, в который будут записаны метаданные XML файлов (это не XSD схема!).
 4. Запустить команду и дождаться завершения ее выполнения.
 5. Выбрать команду "xml2db-convert".
 6. В поле "--schema" выбрать файл, созданный командой "xml2db-schema".
 7. Выбрать в поле "--output-dir" папку, куда будут записаны CSV файлы.
 8. В поле "--out-mode" выбрать "plain" или "compress". В случае "compress" CSV файлы будут запакованы для экономии места на диске.
 9. Запустить команду и дождаться окончания ее выполнения.
 10. Выбрать команду "xml2db-scripts".
 11. В поле "--schema" выбрать файл, созданный командой "xml2db-schema".
 12. Указать адрес сервера и название базы данных в соответствующих полях.
 13. В поле "--output-dir" выбрать папку с CSV файлами.
 14. Выбрать "Yes" напротив "--compressed", если на шаге 8 в "--out-mode" выбрали "compress".
 15. Сбросить выбор XML файлов кнопкой "Clear".
 16. Запустить команду. На этом работа в dufi заканчивается.
 18. Создать таблицы под набор CSV файлов можно с помощью SQL скрипта, который был сгенерирован сомандой "xml2db-scripts".
 19. Загрузить данные в базу можно с помощью скрипта bat.
 20. Написать скрипт для формирования нужной плоской таблицы.
""".strip()


class OracleFixCommand(Command):

    cli_command = "xml2csv"
    cli_command_help = argparse.SUPPRESS  # http://bugs.python.org/issue22848
    cli_files_required = False

    gui_order = 12
    gui_command = "XML to CSV"
    gui_description = "How to convert XML files to tabular using DuFi."

    ############################################################################

    @classmethod
    def _init_gui(cls, app):
        w = app.builder.get_object("TextXML2TSV")
        w.insert(tk.END, TEXT)
        w.configure(state=tk.DISABLED)

    ############################################################################

    @classmethod
    def run(cls, args):
        echo(TEXT)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        pass

    ############################################################################

    @classmethod
    def validate_cmd_args(cls, app):
        raise InvalidCommandArgs("Sssssssssssssss... Boom!")

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        return []
