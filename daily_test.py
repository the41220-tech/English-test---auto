#!/usr/bin/env python3
"""
매일 자동 영단어 테스트 생성 스크립트
- vocabulary_complete.txt에서 랜덤 20개 선택
- Claude API로 테스트 생성
- 노션에 결과 업로드 (2000자 제한 해결)
"""

import os
import re
import random
from datetime import datetime
from anthropic import Anthropic
from notion_client import Client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def select_random_words(vocab_file, count=20):
    """
    단어장에서 랜덤으로 단어 선택
    
    Args:
        vocab_file: vocabulary_complete.txt 파일 경로
        count: 선택할 단어 개수 (기본 20개)
    
    Returns:
        선택된 단어 리스트 [(word, meaning), ...]
    """
    with open(vocab_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and '|' in line]
    
    # 랜덤 선택
    selected_lines = random.sample(lines, min(count, len(lines)))
    
    # 단어와 뜻 분리
    words = []
    for line in selected_lines:
        if '|' in line:
            word, meaning = line.split('|', 1)
            words.append((word.strip(), meaning.strip()))
    
    return words


def generate_test_with_claude(words, api_key):
    """
    Claude API를 사용해 테스트 생성
    
    Args:
        words: [(word, meaning), ...] 형태의 단어 리스트
        api_key: Claude API 키
    
    Returns:
        생성된 테스트 텍스트
    """
    client = Anthropic(api_key=api_key)
    
    # 단어 리스트를 문자열로 변환
    word_list = "\n".join([f"{i+1}. {word} - {meaning}" for i, (word, meaning) in enumerate(words)])
    
    prompt = f"""오늘의 영단어 테스트를 만들어주세요.

**단어 목록:**
{word_list}

**테스트 구성:**

1. **능동적 인출 문제 (20문제)**
   - 1-10번: 한국어 뜻을 보고 영어 단어를 쓰는 문제
   - 11-20번: 영어 단어를 보고 한국어 뜻을 쓰는 문제
   
2. **고난도 4지선다 문제 (3-5문제)**
   - 철자가 비슷한 단어들의 뜻을 비교하는 문제
   - 뜻이 비슷한 단어들을 선지로 활용
   - 특히 헷갈리기 쉬운 단어 위주로 출제
   - 예: Affect vs Effect, Accept vs Except, Prescribe vs Proscribe 등

**형식:**

# 오늘의 영단어 테스트
📅 {datetime.now().strftime("%Y년 %m월 %d일")}

---

## Part 1: 능동적 인출 (주관식)

### 1-10번: 한국어 → 영어
**1. [한국어 뜻]**
답: _______________

**2. [한국어 뜻]**
답: _______________

(10번까지)

### 11-20번: 영어 → 한국어
**11. [영어 단어]**
답: _______________

**12. [영어 단어]**
답: _______________

(20번까지)

---

## Part 2: 고난도 4지선다 (3-5문제)

**1. 다음 중 "[단어A]"의 의미로 옳은 것은? (철자가 비슷한 [단어B]와 혼동 주의)**
① [단어A의 뜻]
② [단어B의 뜻]
③ [비슷한 뜻]
④ [관련 있지만 다른 뜻]

(3-5문제)

---

## 정답

### Part 1 정답
1. [단어]  2. [단어]  3. [단어] ...
11. [뜻]  12. [뜻] ...

### Part 2 정답
1. ①  2. ③  3. ②

---

## 단어 복습
1. [단어] - [의미]
2. [단어] - [의미]
...
"""

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text


def split_text_into_chunks(text, max_length=1800):
    """
    텍스트를 2000자 이하의 청크로 분리 (여유있게 1800자)
    
    Args:
        text: 분리할 텍스트
        max_length: 최대 길이 (기본 1800자)
    
    Returns:
        청크 리스트
    """
    # 줄바꿈 기준으로 분리
    lines = text.split('\n')
    chunks = []
    current_chunk = ""
    
    for line in lines:
        # 현재 청크에 라인을 추가했을 때 길이 확인
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + "\n"
        else:
            # 청크가 너무 길면 현재 청크 저장하고 새 청크 시작
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
    
    # 마지막 청크 추가
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def upload_to_notion(test_content, notion_token, page_id):
    """
    노션 페이지에 테스트 업로드 (2000자 제한 해결)
    
    Args:
        test_content: 테스트 내용 (마크다운)
        notion_token: Notion Integration Token
        page_id: 테스트를 추가할 노션 페이지 ID
    """
    notion = Client(auth=notion_token)
    
    # 오늘 날짜
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 텍스트를 청크로 분리
    chunks = split_text_into_chunks(test_content)
    
    print(f"📊 텍스트를 {len(chunks)}개 블록으로 분리")
    
    # 노션 블록 생성
    children = []
    for i, chunk in enumerate(chunks):
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": chunk
                        }
                    }
                ]
            }
        })
    
    # 새 페이지 생성 (지정된 페이지의 하위 페이지로)
    new_page = notion.pages.create(
        parent={"page_id": page_id},
        properties={
            "title": {
                "title": [
                    {
                        "text": {
                            "content": f"영단어 테스트 - {today}"
                        }
                    }
                ]
            }
        },
        children=children
    )
    
    return new_page


def main():
    """메인 실행 함수"""
    
    print("=" * 60)
    print("🎯 매일 영단어 테스트 생성")
    print("=" * 60)
    
    # 설정 파일에서 API 키 읽기 (또는 환경 변수)
    claude_api_key = os.getenv("CLAUDE_API_KEY")
    notion_token = os.getenv("NOTION_TOKEN")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    
    # API 키가 없으면 입력받기
    if not claude_api_key:
        claude_api_key = input("🔑 Claude API Key: ").strip()
    
    if not notion_token:
        notion_token = input("🔑 Notion Integration Token: ").strip()
    
    if not notion_page_id:
        notion_page_id = input("📄 Notion Page ID: ").strip()
    
    # 단어 선택
    print("\n📚 단어 선택 중...")
    vocab_file = "vocabulary_complete.txt"
    words = select_random_words(vocab_file, count=20)
    print(f"✅ 20개 단어 선택 완료")
    
    # 선택된 단어 출력
    print("\n📝 오늘의 단어:")
    for i, (word, meaning) in enumerate(words, 1):
        print(f"  {i}. {word} - {meaning}")
    
    # 테스트 생성
    print("\n🤖 Claude로 테스트 생성 중...")
    test_content = generate_test_with_claude(words, claude_api_key)
    print("✅ 테스트 생성 완료")
    print(f"📏 테스트 길이: {len(test_content)}자")
    
    # 노션 업로드
    print("\n📤 노션에 업로드 중...")
    try:
        page = upload_to_notion(test_content, notion_token, notion_page_id)
        print(f"✅ 업로드 완료!")
        print(f"🔗 링크: {page['url']}")
    except Exception as e:
        print(f"❌ 노션 업로드 실패: {e}")
        print("\n테스트 내용을 파일로 저장합니다...")
        
        # 파일로 저장
        filename = f"test_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"💾 저장됨: {filename}")
    
    print("\n" + "=" * 60)
    print("✨ 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
