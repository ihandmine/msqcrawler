import requests
import asyncio
import aiohttp

# from yarl import URL
#
# import defaults as settings

from utils.log import logging


def _test_log_func():
    logger = logging.get_logger("test")
    # logger.level("GOU", no=22, color="<yellow>", icon="✔️")
    # logger.level("SNAKY", no=22, color="<yellow>", icon="🐍️   ")
    # logger.log("GOU", "Here we go!")
    # logger.log("SNAKY", "Here we go!")
    logger.info('aaaaaaaa')
    logger.error('aaaaaaaa')
    logger.debug('aaaaaaaa')
    logger.critical('aaaaaaaa')
    logger.warning('aaaaaa')
    logger.trace('aaaaaa')
    logger.success('aaaaaa')


def _test_source_log_func():
    import logging
    logging.INFO

    logging.basicConfig(
        level=logging.INFO,
        # filename='./data/filesort.log',
        # filemode='a',
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    logger = logging.getLogger('test')
    logger.info('bbbbbbbbbbbbb')


def _test_session():
    request = requests.Request()
    request.method = 'GET'
    request.headers = {}
    request.url = 'http://192.168.5.222:9501/'
    session = requests.Session()
    resp = session.prepare_request(request)
    print(session.send(resp).status_code)


def _test_settings():
    print(type('aa').__name__)
    # print(settings.__dict__['DOWNLOADER_MIDDLEWARES'])


async def response():
    url = 'http://www.qiushibaike.com'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            _response = await response.text()
            print(_response)


if __name__ == "__main__":
    # asyncio.run(response())
    # test_session()
    # _test_settings()
    '''
    from multihttp.aio_request import AioRequest

    loop = asyncio.get_event_loop()

    async def run():
        request = AioRequest()
        request.url = 'http://www.qiushibaike.com/text'
        return await request.response

    async def task(callback):
        ta = asyncio.create_task(run())
        ta.add_done_callback(callback)
        await ta

    def hand_data(future):
        from spiders.test.qiushi_spider import QiushiSpider
        resp = future.result()
        # with open('qiushi.html', 'wb') as f:
        #     f.write(resp.encode('utf-8'))
        meta = {}
        qiushi = QiushiSpider(resp, meta)
        for item in qiushi.parse():
            print(item)

    loop.run_until_complete(task(hand_data))
    '''

    _test_log_func()
    _test_source_log_func()
