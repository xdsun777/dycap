# TODO 测试
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from NetCrawler import _Crawler, errors
from time import sleep as sp
from DataIo import Txt
import json


class _TestCrawler(_Crawler):
    def __init__(self):
        super(_TestCrawler, self).__init__()
        # self._option.add_experimental_option("detach", True)
        self._option.add_argument('--headless')

    def _test_setup(self):
        return super(_TestCrawler, self)._setup()


class TsetDy(_TestCrawler):
    def __init__(self):
        super(TsetDy, self).__init__()
        self.urls = Txt().get_urls()
        """获取待采集url"""
        self.keys = Txt().get_keys()
        # 获取关键词
        self.ti = 2
        '''设置暂停时间'''

    def _test_setup(self):
        return super(TsetDy, self)._test_setup()

    @staticmethod
    def _click_login(driver):
        if (driver.find_elements(By.ID, 'RkbQLUok') or driver.find_elements(By.ID, 'b4kMZDrJ')) or driver.find_elements(
                By.ID, 'login-panel-news'):
            return True
        else:
            return False

    @staticmethod
    def get_network_log(drivers,logs: [{}]):
        fans_list = []
        for l in logs:
            nw = json.loads(l.get('message')).get('message')
            if nw.get('method') == 'Network.responseReceived':
                params = nw['params']
                request_url = params['response']['url']
                if 'user/follower/list' in request_url:
                    request_id = params['requestId']
                    response_body = drivers.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    fans_list += json.loads(response_body["body"])["followers"]
                if 'user/following/list' in request_url:
                    request_id = params['requestId']
                    response_body = drivers.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    fans_list += json.loads(response_body["body"])["followings"]
        return fans_list

    def test_fans_activation(self) -> list:
        """
        抓取粉丝关注列表

        约定入口文件：
            待采集的主页链接：running/urls.txt

            筛选关键词：running/keys.txt

            完成采集的主页链接：running/complete_urls.txt

        约定出口文件：
            经关键词筛选后未采集的主页链接：output/urls.txt

            输出采集结果：output/result.xlsx

        :return:list
        """
        test_temp = []

        _driver = self._test_setup()
        for url in self.urls:
            _driver.get(url)

            # 检测是否登录
            while self._click_login(_driver):
                print('请登录')
                sp(self.ti)
            wait = WebDriverWait(_driver, timeout=2, poll_frequency=.2, ignored_exceptions=errors)
            wait.until(lambda d: _driver.find_elements(by=By.CLASS_NAME, value="C1cxu0Vq") or True)
            box2 = [i for i in _driver.find_elements(By.CLASS_NAME, 'C1cxu0Vq')[:2] if i.text != '0']
            for i in box2:
                i.click()
                if _driver.find_elements(By.ID, value="toastContainer"):
                    print('隐私用户')
                    break
                # 滑动粉丝关注列表
                sp(self.ti)
                temp = 0
                while temp < len(_driver.find_elements(By.CLASS_NAME, value="i5U4dMnB")):
                    sp(self.ti - 1)
                    try:
                        ls = _driver.find_elements(By.CLASS_NAME, value="i5U4dMnB")
                        ActionChains(_driver).scroll_to_element(ls[-1]).perform()
                        print(len(ls))
                        temp = len(ls)
                    except:
                        print("关注粉丝列表为空，无法获取！")
                test_temp +=self.get_network_log(_driver, _driver.get_log('performance'))
                if _driver.find_elements(By.CLASS_NAME, value="vc-captcha-close-btn"):
                    _driver.find_element(By.CLASS_NAME, value="vc-captcha-close-btn").click()
                _driver.find_element(by=By.CLASS_NAME, value='KArYflhI').click()
        return test_temp


if __name__ == '__main__':
    t = TsetDy()
    log = t.test_fans_activation()
    print(log)


