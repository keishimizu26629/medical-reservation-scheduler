import os
from datetime import datetime, timedelta
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebTest:
    def __init__(self, url: str, headless: bool = True):
        self.url = url
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        # ChromeDriverのパスを環境変数から取得（設定されていない場合はデフォルトを使用）
        self.chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', 'chromedriver')

    def run_test(self, target_time: datetime, form_data: dict):
        # 指定時間の30分前に開始
        wait_time = target_time - timedelta(minutes=30)
        current_time = datetime.now()

        if current_time < wait_time:
            sleep_seconds = (wait_time - current_time).total_seconds()
            sleep(sleep_seconds)

        # ブラウザ起動
        driver = webdriver.Chrome(options=self.options)

        # ページにアクセス
        driver.get(self.url)

        # フォームの入力
        # ID指定での入力
        if 'c_code' in form_data:
            code_element = driver.find_element(By.ID, 'c_code')
            code_element.send_keys(form_data['c_code'])

        if 'c_pass' in form_data:
            pass_element = driver.find_element(By.ID, 'c_pass')
            pass_element.send_keys(form_data['c_pass'])

        # その他のフォーム項目の入力
        for field, value in form_data.items():
            if field not in ['c_code', 'c_pass']:
                element = driver.find_element(By.NAME, field)
                element.send_keys(value)

        # 指定時間まで待機
        current_time = datetime.now()
        if current_time < target_time:
            sleep_seconds = (target_time - current_time).total_seconds()
            sleep(sleep_seconds)

        # 送信ボタンクリック
        submit_button = driver.find_element(By.CSS_SELECTOR, 'input[name="bOK"][type="submit"]')
        submit_button.click()

        # 次のページのOKボタンが表示されるまで待機（最大10秒）
        wait = WebDriverWait(driver, 10)
        ok_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="submit"][name="bOK"][value="OK"]'))
        )
        ok_button.click()

        # 「一般診療」リンクが表示されるまで待機（最大10秒）
        general_link = wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "一般診療")]'))
        )
        general_link.click()

        # 「【同意する】」リンクが表示されるまで待機（最大10秒）
        agree_link = wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(., "【同意する】")]'))
        )
        agree_link.click()

        # 「午前の診察（一人分）」リンクが表示されるまで待機（最大10秒）
        morning_link = wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "午前の診察（一人分）")]'))
        )
        morning_link.click()

        # ul.clearfix内の最初のli要素内のリンクが表示されるまで待機（最大10秒）
        first_time_slot = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.clearfix li:first-child a'))
        )
        first_time_slot.click()

        # 「予約確定」リンクが表示されるまで待機（最大10秒）
        # confirm_link = wait.until(
        #     EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "予約確定")]'))
        # )
        # confirm_link.click()

        # ブラウザを開いたままにする（ユーザーが手動で閉じるまで待機）
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            driver.quit()

# 使用例
if __name__ == "__main__":
    # テスト設定
    # 実際の予約サイトのURLに変更してください
    TEST_URL = "https://ssc2.doctorqube.com/nakano-kids-hospital/input.cgi?vMode=mode_book&stamp=1737580669942"

    # 予約実行時刻の設定（30分前から待機を開始します）
    TARGET_TIME = datetime(2025, 1, 23, 7, 8)  # 7時7分

    # フォームデータの設定
    # 実際のフォーム要素のname属性に合わせて変更してください
    FORM_DATA = {
        "c_code": "342203",  # 会員コード
        "c_pass": "0831",    # パスワード
        # その他のフォーム項目を追加
    }

    # テスト実行
    # ヘッドレスモード（画面表示なし）
    # test = WebTest(TEST_URL, headless=True)
    # test.run_test(TARGET_TIME, FORM_DATA)

    # 表示モード（ブラウザ画面表示あり）
    test = WebTest(TEST_URL, headless=False)
    test.run_test(TARGET_TIME, FORM_DATA)
