import time
import re
from collections import defaultdict
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


def build_search_url(keyword, school_name="광운인공지능고등학교", prov_code="B10", neis_code="B100000580"):
    base_url = "https://read365.edunet.net/PureScreen/SchoolSearchResult"
    keyword_encoded = quote(keyword)
    school_encoded = quote(school_name)
    return f"{base_url}?searchKeyword={keyword_encoded}&provCode={prov_code}&neisCode={neis_code}&schoolName={school_encoded}"


def fetch_book_data(keyword="문명", max_results=5):
    # Selenium 설정
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")  # 헤드리스 모드 추가
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(options=chrome_options)

    try:
        search_url = build_search_url(keyword)
        driver.get(search_url)

        wait = WebDriverWait(driver, 20)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)

        book_data = []
        seen = defaultdict(int)
        unique_keys = dict()
        idx = 0

        detail_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.hover-btn.plus")))

        while len(unique_keys) < max_results and idx < len(detail_buttons):
            try:
                detail_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.hover-btn.plus")))
                btn = detail_buttons[idx]
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)

                img_tag = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='도서의 표지 이미지입니다.']")))
                image_url = img_tag.get_attribute("src")

                author = driver.find_element(By.XPATH, "//span[contains(text(), '저자:')]").text.replace("저자: ", "")
                publisher = driver.find_element(By.XPATH, "//span[contains(text(), '출판사:')]").text.replace("출판사: ", "")
                call_number = driver.find_element(By.XPATH, "//span[contains(text(), '청구기호:')]").text.replace("청구기호: ", "")
                availability = driver.find_element(By.CSS_SELECTOR, ".book-state").text.strip()

                try:
                    title = driver.find_element(By.CSS_SELECTOR, "h3.prod-name").text.strip()
                except:
                    title = "제목 정보 없음"

                try:
                    description = driver.find_element(By.CSS_SELECTOR, "p.more-area").text.strip()
                except NoSuchElementException:
                    description = "도서 소개 없음"

                key = (title, author, publisher)
                seen[key] += 1

                if key not in unique_keys:
                    unique_keys[key] = {
                        "제목": title,
                        "저자": author,
                        "출판사": publisher,
                        "청구기호": call_number,
                        "대출 가능 여부": availability,
                        "표지 이미지": image_url,
                        "도서 소개": description,
                        "권 수": seen[key]
                    }
                else:
                    unique_keys[key]["권 수"] = seen[key]

                driver.back()
                time.sleep(1)
                wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                time.sleep(0.5)
                idx += 1

            except StaleElementReferenceException:
                idx += 1
            except Exception as inner_e:
                print(f"❌ 오류 발생: {inner_e}")
                idx += 1

        # 제목 내 숫자 정렬 기준 함수
        def extract_volume(title):
            match = re.search(r"\.\s*(\d+)$", title)
            return int(match.group(1)) if match else 0

        sorted_books = sorted(
            unique_keys.values(),
            key=lambda x: (re.sub(r"\.\s*\d+$", "", x["제목"]), extract_volume(x["제목"]))
        )

        return sorted_books

    except Exception as e:
        print("❌ 전체 오류 발생:", e)
        return []

    finally:
        driver.quit()
