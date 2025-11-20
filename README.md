# 📚 영단어 테스트 자동화 시스템
## Mac 설치 및 실행 가이드

---

## 📦 Step 1: 프로젝트 설정

### 1-1. 프로젝트 폴더 만들기
```bash
# 터미널 열기 (Command + Space → "터미널" 입력)

# 프로젝트 폴더 생성
mkdir ~/vocab-test
cd ~/vocab-test
```

### 1-2. 파일 복사하기
다운로드한 모든 파일을 `~/vocab-test` 폴더에 복사:
- `combined.txt` (원본 단어 파일)
- `clean_words.py`
- `setup_vocabulary.py`
- `daily_test.py`
- `requirements.txt`
- `.env.example`

---

## 🔧 Step 2: Python 환경 설정

### 2-1. Python 버전 확인
```bash
python3 --version
# Python 3.8 이상이어야 합니다
```

### 2-2. 가상환경 생성
```bash
cd ~/vocab-test
python3 -m venv venv
source venv/bin/activate
```

### 2-3. 라이브러리 설치
```bash
pip install -r requirements.txt
```

---

## 🔑 Step 3: API 키 설정

### 3-1. Claude API 키 발급
1. https://console.anthropic.com/ 접속
2. 로그인
3. **Settings → API Keys**
4. **Create Key** 클릭
5. 키 복사

### 3-2. Notion Integration 만들기
1. https://www.notion.so/my-integrations 접속
2. **+ New integration** 클릭
3. 이름 입력 (예: "Vocab Test")
4. **Submit** 클릭
5. **Internal Integration Token** 복사

### 3-3. Notion 페이지 설정
1. 노션에서 새 페이지 만들기 (예: "영단어 테스트")
2. 페이지 우측 상단 **⋯ → Connections → Connect to [만든 Integration]**
3. 페이지 URL에서 Page ID 복사
   ```
   https://notion.so/My-Page-abc123def456?v=...
                          ↑ 이 부분이 Page ID
   ```

### 3-4. .env 파일 만들기
```bash
cd ~/vocab-test
cp .env.example .env
nano .env  # 또는 텍스트 에디터로 열기
```

`.env` 파일 내용을 실제 값으로 수정:
```
CLAUDE_API_KEY=sk-ant-api03-실제키입력
NOTION_TOKEN=secret_실제토큰입력
NOTION_PAGE_ID=abc123def456
```

저장하고 닫기 (nano: Ctrl+O → Enter → Ctrl+X)

---

## ▶️ Step 4: 실행하기

### 4-1. 단어 정리 (1회만)
```bash
cd ~/vocab-test
source venv/bin/activate
python3 clean_words.py
```

출력:
```
✅ 총 1753개 단어 발견
💾 저장 완료: words_cleaned.txt
```

### 4-2. 한국어 뜻 추가 (1회만)
```bash
python3 setup_vocabulary.py
```

- API 키 입력 요청되면 입력
- 약 5-10분 소요
- 비용: 약 $0.30-0.50

출력:
```
✅ 완료! 1753개 단어 처리됨
📁 최종 파일: vocabulary_complete.txt
```

### 4-3. 테스트 생성 (매일)
```bash
python3 daily_test.py
```

출력:
```
✅ 20개 단어 선택 완료
✅ 테스트 생성 완료
✅ 업로드 완료!
🔗 링크: https://notion.so/...
```

---

## ⏰ Step 5: 자동 실행 설정

### 5-1. 실행 스크립트 만들기
```bash
cd ~/vocab-test
nano run_daily_test.sh
```

다음 내용 입력:
```bash
#!/bin/bash
cd ~/vocab-test
source venv/bin/activate
python3 daily_test.py
```

저장 후 실행 권한 부여:
```bash
chmod +x run_daily_test.sh
```

### 5-2. Cron Job 설정 (매일 오전 9시)
```bash
crontab -e
```

다음 라인 추가:
```
0 9 * * * ~/vocab-test/run_daily_test.sh >> ~/vocab-test/log.txt 2>&1
```

저장하고 닫기 (vim: :wq)

### 5-3. Cron 확인
```bash
crontab -l
```

---

## 🧪 테스트 실행

수동으로 한번 실행해보기:
```bash
cd ~/vocab-test
./run_daily_test.sh
```

로그 확인:
```bash
cat ~/vocab-test/log.txt
```

---

## 🎯 시간대별 실행 설정

### 매일 오전 8시
```
0 8 * * * ~/vocab-test/run_daily_test.sh >> ~/vocab-test/log.txt 2>&1
```

### 매일 오후 7시
```
0 19 * * * ~/vocab-test/run_daily_test.sh >> ~/vocab-test/log.txt 2>&1
```

### 평일만 오전 9시
```
0 9 * * 1-5 ~/vocab-test/run_daily_test.sh >> ~/vocab-test/log.txt 2>&1
```

---

## ❓ 문제 해결

### 오류 1: "venv not found"
```bash
cd ~/vocab-test
python3 -m venv venv
```

### 오류 2: "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 오류 3: "Notion API error"
- 노션 페이지에 Integration이 연결되어 있는지 확인
- Page ID가 정확한지 확인

### 오류 4: "Claude API error"
- API 키가 정확한지 확인
- 결제 정보가 등록되어 있는지 확인
- https://console.anthropic.com/settings/billing

---

## 💰 예상 비용

### 초기 설정 (1회)
- 1,753개 단어 뜻 추가: **약 $0.30-0.50**

### 매일 운영
- 20개 단어 테스트 생성: **약 $0.003/일**
- 월 비용: **약 $0.10** (30일 기준)

---

## 📊 파일 구조

```
~/vocab-test/
├── combined.txt              # 원본 단어 파일
├── words_cleaned.txt         # 정리된 단어 (Step 4-1 후)
├── vocabulary_complete.txt   # 뜻 추가된 최종 파일 (Step 4-2 후)
├── clean_words.py           # 단어 정리 스크립트
├── setup_vocabulary.py      # 뜻 추가 스크립트
├── daily_test.py           # 테스트 생성 스크립트
├── run_daily_test.sh       # 자동 실행 스크립트
├── requirements.txt        # Python 라이브러리
├── .env                    # API 키 (직접 만들기)
├── venv/                   # Python 가상환경
└── log.txt                # 실행 로그
```

---

## ✨ 완료!

이제 매일 자동으로:
1. 20개 랜덤 단어 선택
2. Claude가 테스트 생성
3. 노션에 자동 업로드

노션에서 테스트 확인하고 공부하세요! 🎉
