# coding=utf-8

from util.struct import Configure


class _Config(Configure):

    def _init_options(self):


        # 活动开始时间

        self.Start = self._parser.getstr(r'PrizeTime', r'Start')

        self.Long = self._parser.getint(r'PrizeTime', r'Long')

        # 每日抽奖最大次数

        self.TotalChance = self._parser.getint(r'PrizeChanceInfo', r'TotalChance')
        self.EveryChanceRequire = self._parser.getint(r'PrizeChanceInfo', r'EveryChanceRequire')

        # 基本

        self.Port = self._parser.getint(r'Base', r'Port')

        self.Debug = self._parser.getboolean(r'Base', r'Debug')

        self.GZip = self._parser.getboolean(r'Base', r'GZip')

        self.Secret = self._parser.get(r'Base', r'Secret')

        self.AccessControlAllowOrigin = self._parser.get(r'Base', r'AccessControlAllowOrigin')


        # 日志

        self.LogLevel = self._parser.get(r'Log', r'LogLevel')

        self.LogFilePath = self._parser.get(r'Log', r'LogFilePath')

        self.LogFileBackups = self._parser.getint(r'Log', r'LogFileBackups')


        # mysql数据库

        self.MySqlMaster = self._parser.get_split_host(r'MySql', r'MySqlServer')

        self.MySqlUser = self._parser.get(r'MySql', r'MySqlUser')

        self.MySqlPasswd = self._parser.get(r'MySql', r'MySqlPasswd')

        self.MySqlMinConn = self._parser.getint(r'MySql', r'MySqlMinConn')

        self.MySqlMaxConn = self._parser.getint(r'MySql', r'MySqlMaxConn')

        self.MySqlDbName = self._parser.get(r'MySql', r'MySqlDbName')


        # mssql

        self.MssqlHost = self._parser.get_split_host(r'Mssql', r'MssqlHost')

        self.MssqlUser = self._parser.get(r'Mssql', r'MssqlUser')

        self.MssqlPasswd = self._parser.get(r'Mssql', r'MssqlPasswd')


        self.MssqlAccountDbName = self._parser.get(r'Mssql', r'MssqlAccountDbName')

        self.MssqlRecordDbName = self._parser.get(r'Mssql', r'MssqlRecordDbName')

        # self.MssqlTreasureDbName = self._parser.get(r'Mssql', r'MssqlTreasureDbName')



        # 缓存

        self.RedisHost = self._parser.get_split_host(r'Redis', r'RedisHost')

        self.RedisBase = self._parser.getint(r'Redis', r'RedisBase')

        self.RedisPasswd = self._parser.getstr(r'Redis', r'RedisPasswd')

        self.RedisMinConn = self._parser.getint(r'Redis', r'RedisMinConn')

        self.RedisMaxConn = self._parser.getint(r'Redis', r'RedisMaxConn')


        # 事件总线

        self.EventBusChannels = self._parser.getint(r'Event', r'EventBusChannels')


        # HTTP访问

        self.HttpErrorAutoRetry = self._parser.getint(r'Http', r'HttpErrorAutoRetry')

        self.HttpConnectTimeout = self._parser.getfloat(r'Http', r'HttpConnectTimeout')

        self.HttpRequestTimeout = self._parser.getfloat(r'Http', r'HttpRequestTimeout')



        # 微信

        self.WeixinAppId = self._parser.get(r'Weixin', r'WeixinAppId')

        self.WeixinAppSecret = self._parser.get(r'Weixin', r'WeixinAppSecret')

        self.WeixinPayMchId = self._parser.get(r'Weixin', r'WeixinPayMchId')

        self.WeixinPayApiKey = self._parser.get(r'Weixin', r'WeixinPayApiKey')

        self.WeixinAPIRetry = self._parser.getint(r'Weixin', r'WeixinAPIRetry')


        # 短信签名（free sign）

        self.SMSFreeSign = self._parser.get(r'SMS', r'FreeSign')


        # 时间设置

        self.RedisExpires = self._parser.getint(r'Time', r'RedisExpires')

        self.TokenRefreshTimeLimit = self._parser.getint(r'Time', r'TokenRefreshTimeLimit')

        self.SmsValidTimeLimit = self._parser.getint(r'Time', r'SmsValidTimeLimit')

        self.SmsSendTimeLimit = self._parser.getint(r'Time', r'SmsSendTimeLimit')

        self.LoginExpires = self._parser.getint(r'Time', r'LoginExpires')

        self.FuncCacheExpires = self._parser.getint(r'Time', r'FuncCacheExpires')

        self.LocalCacheExpires = self._parser.getint(r'Time', r'LocalCacheExpires')

        self.WeixinAccessTokenExpire = self._parser.getint(r'Time', r'WeixinAccessTokenExpire')

        self.AcquireDistributedLockTimeout = self._parser.getint(r'Time', r'AcquireDistributedLockTimeout')

        self.DistributedLockMaxHoldTime = self._parser.getint(r'Time', r'DistributedLockMaxHoldTime')


        # Interface

        self.WeixinPayNotifyUrl = self._parser.get(r'Interface', r'WeixinPayNotifyUrl')



Config = _Config()





