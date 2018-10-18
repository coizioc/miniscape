class TradeError(Exception):
    def __init__(self, message):
        self.msg = message
