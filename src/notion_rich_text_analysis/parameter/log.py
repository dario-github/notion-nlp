# -*- encoding: utf-8 -*-
"""日志封装的库, 使用 config_log 配置日志"""
from __future__ import absolute_import, print_function, unicode_literals

import getpass
import json
import logging
import platform
from logging import Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

TRACE = 31
STATS = 32
monitor_logger = logging.getLogger("monitor")  # type: logging.Logger
monitor_logger.propagate = False


def config_log(
    project,
    module,
    log_root=None,
    app_id="",
    level=logging.INFO,
    print_terminal=False,
    enable_monitor=True,
):  # pylint: disable=too-many-arguments
    """配置日志, 日志存放在 log_root / project / f'{module}.log'
    配置完成后，会存在两种日志
    #. 普通日志
        ::
            import logging
            logging.info("some info message")
            logging.warn("some warn message")
            logging.error("some error message")
    #. monitor 日志
        ::
            import logging
            logging.trace("uid_001", "mongo_reader", info="some thing happend.", reason="some reason or stack")
            logging.stats("uid_001", "mongo_writer", count=9, success=9, error=0, type="create")
        **OR** ::
            import logging
            tracer = logging.monitor("uid_001", "mongo_reader")
            tracer.trace(info="some thing happend.", reason="some reason")
            tracer.stats(count=9, success=9, error=0)
        **OR** ::
            from log import Monitor
            tracer = Monitor("uid_001", "mongo_reader")
            tracer.trace(info="some thing happend.", reason="some reason")
            tracer.stats(count=9, success=9, error=0)
    Args:
        @param log_root: 日志打印目录
        @param project_id: 项目id, 会作为日志名称
        @param module: 模块名称，会作为日志名称
        @param level: 日志打印级别
        @param print_terminal: 是否输出到终端，调试用
        @param enable_monitor: 是否启用monitor，默认启用。
    """
    logging.addLevelName(TRACE, "TRACE")
    logging.addLevelName(STATS, "STATS")

    if log_root is None:
        log_root = user_log_path()
    else:
        log_root = Path(log_root)
    (log_root / project).mkdir(parents=True, exist_ok=True)

    log_file = log_root / project / "{module}.log".format(module=module)
    handlers = [TimedRotatingFileHandler(log_file, when="D")]
    if print_terminal:
        handlers.append(StreamHandler())

    logging.basicConfig(
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(process)s] [%(filename)s] [%(lineno)s] [%(message)s]",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
        handlers=handlers,
    )

    if enable_monitor:
        (log_root / project / "monitor").mkdir(parents=True, exist_ok=True)
        monitor_file = log_root / project / "monitor" / "monitor.log"

        monitor_handlers = [TimedRotatingFileHandler(monitor_file, when="D")]
        if print_terminal:
            monitor_handlers.append(StreamHandler())

        formatter = Formatter(
            fmt="[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(trace_id)s] [{app_id}] [%(module_name)s] [%(message)s]".format(
                app_id=app_id
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        for handler in monitor_handlers:
            handler.setFormatter(formatter)
            monitor_logger.addHandler(handler)
        monitor_logger.setLevel(logging.CRITICAL + 1)
        logging.trace = _trace
        logging.stats = _stats
        logging.monitor = _monitor


def user_log_path():
    """
    获取用户日志目录, 通常是 /logs/{username}, 如果不存在则会尝试自动创建。
    如果这个目录无法使用，则使用 /home/{username}/logs
    WARNING: 一般来说，这个函数执行的时候，logging还没有初始化，不要在这个函数里面加logging打印。
    """
    user = getpass.getuser()
    if not user:
        user = Path.home().name
    if platform.system() != "Windows":
        path = Path("/logs") / user
        if not path.exists():
            try:
                path.mkdir(exist_ok=True, parents=True)
            except OSError:
                # 可能没有权限创建，就放弃
                pass
        if path.is_dir():
            return path
    if hasattr(Path, "home"):
        path = Path.home() / "logs"
    else:
        path = Path("logs")
    if not path.exists():
        path.mkdir(parents=True)
    return path


class Monitor:
    __slots__ = ["trace_id", "module_name"]

    def __init__(self, trace_id="", module_name=""):
        self.trace_id = trace_id
        self.module_name = module_name

    def _convert(self, value):
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    def _construct_message(self, **kwargs):
        return json.dumps(
            {k: self._convert(v) for k, v in kwargs.items()}, ensure_ascii=False
        )

    def trace(self, **kwargs):
        monitor_logger._log(
            TRACE,
            self._construct_message(**kwargs),
            args=(),
            extra={"trace_id": self.trace_id, "module_name": self.module_name},
        )

    def stats(self, **kwargs):
        monitor_logger._log(
            STATS,
            self._construct_message(**kwargs),
            args=(),
            extra={"trace_id": self.trace_id, "module_name": self.module_name},
        )


def _trace(trace_id="", module_name="", **kwargs):
    return Monitor(trace_id, module_name).trace(**kwargs)


def _stats(trace_id="", module_name="", **kwargs):
    return Monitor(trace_id, module_name).stats(**kwargs)


def _monitor(trace_id="", module_name=""):
    return Monitor(trace_id, module_name)
