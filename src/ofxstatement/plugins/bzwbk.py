#!/usr/bin/env python3
import csv
from datetime import datetime
from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import generate_transaction_id


class BZWBKCSVParser(CsvStatementParser):
    date_format = "%d-%m-%Y"

    mappings = {
        "date": 0,
        "payee": 2,
        "memo": 3,
        "amount": 5,
    }

    def __init__(self, *args, **kwargs):
        super(BZWBKCSVParser, self).__init__(*args, **kwargs)
        self.first_line_skipped = False

    def parse(self):
        return super(BZWBKCSVParser, self).parse()

    def split_records(self):
        return csv.reader(self.fin, delimiter=",")

    def parse_record(self, line):
        if not self.first_line_skipped:
            self.first_line_skipped = True
            return None
        self.statement.currency = "PLN"

        line[5] = line[5].replace(",",".")
        stmtline = super(BZWBKCSVParser, self).parse_record(line)
        stmtline.trntype = "DEBIT" if stmtline.amount < 0 else "CREDIT"
        stmtline.id = generate_transaction_id(stmtline)

        self.statement.start_date = datetime.strptime(line[0], self.date_format)
        self.statement.start_balance = float(line[6].replace(",","."))
        if not self.statement.end_date:
            self.statement.end_date = datetime.strptime(line[0], self.date_format)
        if not self.statement.end_balance:
            self.statement.end_balance = float(line[6].replace(",","."))
        return stmtline


class BZWBKPlugin(Plugin):
    def get_parser(self, filename):
        encoding = self.settings.get("charset", "utf8")
        f = open(filename, "r", encoding=encoding)
        parser = BZWBKCSVParser(f)
        parser.statement.account_id = self.settings["account"]
        parser.statement.bank_id = self.settings.get("bank", "bzwbk")
        return parser
