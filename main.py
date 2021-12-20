from blitzmanager import logger, ArgumentsParser, Runner, Path, FlagObserver, CMakeArguments
import os

cwd = os.path.dirname(os.path.realpath(__file__))


class Observer(FlagObserver):
    def flag_set(self, flag: str, value: object):
        """

        :param flag:
        :param value:
        :return:
        """
        logger.info(f"FLags : {flag}, {value}")


if __name__ == '__main__':
    parser = ArgumentsParser(description="BlitzManager is a tool for manging C/C++ dependencies.")
    parser.add_flag("--port", required=False, default=None, type=int)
    runner = Runner(parser)
    observer = Observer()
    runner.add_flag_observer("port", observer)
    runner.run(Path(cwd, "out"))
    runner.notify_flag_observers()
    manager = runner.managers()[0]
    runner.builder().build_via_package_manager("zlib", manager)
    args = CMakeArguments(Path(cwd, "out", "install"))
    runner.builder().build_from_source("Dummy", Path(cwd, "Dummy"), args)
