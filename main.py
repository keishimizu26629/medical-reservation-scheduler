import os
from datetime import datetime, timedelta
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging

class WebTest:
    def __init__(self, url: str, headless: bool = True):
        self.url = url
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        # ChromeDriverのパスを環境変数から取得(設定されていない場合はデフォルトを使用)
        self.chrome_driver_path = os.getenv('CHROME_DRIVER_PATH', 'chromedriver')

    def find_and_input(self, driver, by, value, input_value, field_name, required=True):
        try:
            element = driver.find_element(by, value)
            element.send_keys(input_value)
            logging.info(f"{field_name}の入力成功")
            return True
        except NoSuchElementException:
            if required:
                logging.error(f"{field_name}の要素が見つかりませんでした: {value}")
                raise
            else:
                logging.info(f"{field_name}の要素が見つかりませんでした(オプショナル): {value}")
                return False

    def find_and_click(self, driver, wait, by, value, element_name, timeout=10, required=True):
        try:
            element = wait.until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            logging.info(f"{element_name}をクリックしました")
            return True
        except Exception as e:
            if required:
                logging.error(f"{element_name}のクリックに失敗しました: {str(e)}")
                raise
            else:
                logging.info(f"{element_name}は見つかりませんでした(オプショナル)")
                return False

    def run_test(self, target_time: datetime, form_data: dict, department: str = None, is_first_time: bool = False):
        # ログ設定
        logging.basicConfig(level=logging.INFO)

        # 指定時間の30分前に開始
        wait_time = target_time - timedelta(minutes=30)
        current_time = datetime.now()

        if current_time < wait_time:
            sleep_seconds = (wait_time - current_time).total_seconds()
            sleep(sleep_seconds)

        # ブラウザ起動
        driver = webdriver.Chrome(options=self.options)
        wait = WebDriverWait(driver, 10)

        try:
            # 初期ページにアクセス
            driver.get(self.url)
            logging.info("初期ページにアクセスしました")

            # 「予約をとる」ボタンをクリック
            self.find_and_click(
                driver, wait,
                By.XPATH,
                '//a[.//span[contains(text(), "予約をとる")]]',
                "予約をとるボタン"
            )

            # 初回か2回目以降かの選択
            if is_first_time:
                # 初回の場合
                self.find_and_click(
                    driver, wait,
                    By.XPATH,
                    '//a[contains(@href, "mode_new")]',
                    "初回予約ボタン"
                )
            else:
                # 2回目以降の場合
                self.find_and_click(
                    driver, wait,
                    By.XPATH,
                    '//a[contains(@href, "mode_book")]',
                    "2回目以降予約ボタン"
                )

            # フォームの入力
            if is_first_time:
                # 初回予約の場合の入力フィールド
                if 'name' in form_data:
                    self.find_and_input(driver, By.NAME, 'Ptel', form_data['name'], '名前')

                if 'kana' in form_data:
                    self.find_and_input(driver, By.NAME, 'Kana', form_data['kana'], 'フリガナ', required=False)

                if 'tel' in form_data:
                    self.find_and_input(driver, By.NAME, 'TelNo', form_data['tel'], '電話番号')

                if 'birth_date' in form_data:
                    # 生年月日フィールドの入力を試みる(複数の可能性のある属性名で試行)
                    for birth_field_name in ['Birth', 'BirthDay', 'Birthday', 'birth_date']:
                        if self.find_and_input(driver, By.NAME, birth_field_name, form_data['birth_date'], '生年月日'):
                            break

                if 'sex' in form_data:
                    self.find_and_input(driver, By.NAME, 'Sex', form_data['sex'], '性別')

                if 'email' in form_data:
                    self.find_and_input(driver, By.NAME, 'Email', form_data['email'], 'メールアドレス')
            else:
                # 2回目以降の予約の場合
                if 'c_code' in form_data:
                    self.find_and_input(driver, By.ID, 'c_code', form_data['c_code'], '会員コード')

                if 'c_pass' in form_data:
                    self.find_and_input(driver, By.ID, 'c_pass', form_data['c_pass'], 'パスワード')

            # その他のフォーム項目の入力
            for field, value in form_data.items():
                if field not in ['c_code', 'c_pass', 'name', 'kana', 'tel', 'birth_date', 'sex', 'email']:
                    try:
                        element = driver.find_element(By.NAME, field)
                        element.send_keys(value)
                    except NoSuchElementException:
                        continue

            # 指定時間まで待機
            current_time = datetime.now()
            if current_time < target_time:
                sleep_seconds = (target_time - current_time).total_seconds()
                sleep(sleep_seconds)

            # 送信ボタンクリック
            self.find_and_click(
                driver, wait,
                By.CSS_SELECTOR,
                'input[name="bOK"][type="submit"]',
                "送信ボタン"
            )

            # 次のページのOKボタンをクリック
            self.find_and_click(
                driver, wait,
                By.CSS_SELECTOR,
                'input[type="submit"][name="bOK"][value="OK"]',
                "OKボタン"
            )

            # 科の選択(指定されている場合)
            if department:
                try:
                    # 科選択のリンクを探して、一致するものをクリック
                    department_xpath = f'//a[contains(text(), "{department}")]'
                    self.find_and_click(
                        driver, wait,
                        By.XPATH,
                        department_xpath,
                        f"{department}のリンク",
                        timeout=5,
                        required=False
                    )
                except TimeoutException:
                    logging.info("科選択ページはスキップされました")

            # 「一般診療」リンクをクリック
            self.find_and_click(
                driver, wait,
                By.XPATH,
                '//a[contains(text(), "一般診療")]',
                "一般診療リンク"
            )

            # 「【同意する】」リンクをクリック
            self.find_and_click(
                driver, wait,
                By.XPATH,
                '//a[contains(., "【同意する】")]',
                "同意するリンク"
            )

            # 「午前の診察(一人分)」リンクをクリック
            # より汎用的な要素の特定方法を使用
            morning_xpath_patterns = [
                '//a[contains(text(), "午前の診察") and contains(text(), "一人分")]',
                '//div[contains(@class, "date")]//a[contains(text(), "午前の診察")]',
                '//li//a[contains(text(), "午前の診察")]'
            ]

            clicked = False
            for xpath in morning_xpath_patterns:
                if self.find_and_click(driver, wait, By.XPATH, xpath, "午前の診察リンク", required=False):
                    clicked = True
                    break

            if not clicked:
                logging.error("午前の診察リンクが見つかりませんでした")
                raise NoSuchElementException("午前の診察リンクが見つかりませんでした")

            # ul.clearfix内の最初のli要素内のリンクをクリック
            self.find_and_click(
                driver, wait,
                By.CSS_SELECTOR,
                'ul.clearfix li:first-child a',
                "時間枠"
            )

            # 「予約確定」リンクが表示されるまで待機（最大10秒）
            # confirm_link = wait.until(
            #     EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "予約確定")]'))
            # )
            # confirm_link.click()

            # ブラウザを開いたままにする(ユーザーが手動で閉じるまで待機)
            try:
                while True:
                    sleep(1)
            except KeyboardInterrupt:
                driver.quit()

        except Exception as e:
            logging.error(f"エラーが発生しました: {str(e)}")
            driver.quit()
            raise

# 使用例
if __name__ == "__main__":
    # テスト設定
    # 実際の予約サイトのURLに変更してください
    TEST_URL = "https://ssc2.doctorqube.com/nakano-kids-hospital/"  # URLを初期ページに変更

    # 予約実行時刻の設定(30分前から待機を開始します)
    TARGET_TIME = datetime(2025, 1, 23, 7, 8)  # 7時8分

    # 初回予約の場合のフォームデータ
    FIRST_TIME_FORM_DATA = {
        "name": "中野 太郎",
        "kana": "ナカノ タロウ",  # フリガナを追加
        "tel": "09012345678",
        "birth_date": "20200101",
        "sex": "男",
        "email": "taro@example.com"
    }

    # 2回目以降の予約の場合のフォームデータ
    REGULAR_FORM_DATA = {
        "c_code": "888888",  # 会員コード
        "c_pass": "0101",    # パスワード
    }

    # テスト実行
    # ヘッドレスモード（画面表示なし）
    # test = WebTest(TEST_URL, headless=True)
    # test.run_test(TARGET_TIME, FORM_DATA)

    # 表示モード（ブラウザ画面表示あり）
    test = WebTest(TEST_URL, headless=False)

    # 初回予約の場合(皮膚科を指定)
    test.run_test(TARGET_TIME, FIRST_TIME_FORM_DATA, department="皮膚科", is_first_time=True)

    # 2回目以降の予約の場合
    # test.run_test(TARGET_TIME, REGULAR_FORM_DATA, department="皮膚科", is_first_time=False)
