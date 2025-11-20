#!/usr/bin/env python3
"""
단어에 한국어 뜻 추가 스크립트
- Claude API 사용
- 100개씩 배치 처리
- vocabulary_complete.txt 생성
"""

import os
from anthropic import Anthropic

def add_meanings_to_words(input_file, output_file, api_key):
    """
    단어에 한국어 뜻을 추가하는 함수
    
    Args:
        input_file: 깨끗한 단어 리스트 파일
        output_file: 뜻이 추가된 최종 파일
        api_key: Claude API 키
    """
    
    # API 클라이언트 생성
    client = Anthropic(api_key=api_key)
    
    # 단어 읽기
    print(f"📖 단어 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    
    total_words = len(words)
    print(f"✅ 총 {total_words}개 단어 발견")
    
    # 배치 크기 설정 (한 번에 처리할 단어 개수)
    batch_size = 100
    results = []
    
    # 배치별로 처리
    for i in range(0, total_words, batch_size):
        batch = words[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_words + batch_size - 1) // batch_size
        
        print(f"\n🔄 배치 {batch_num}/{total_batches} 처리 중... ({len(batch)}개 단어)")
        
        # Claude에게 요청할 프롬프트
        prompt = f"""다음 영어 단어들의 한국어 뜻을 제공해주세요.

단어 목록:
{chr(10).join(batch)}

형식:
각 단어마다 정확히 다음 형식으로 답변해주세요:
단어|한국어 뜻

규칙:
1. 각 줄은 반드시 "단어|뜻" 형식
2. 뜻은 간결하게 (2-4개 단어)
3. 여러 의미가 있으면 가장 일반적인 의미만
4. 다른 설명 없이 오직 이 형식만 사용

예시:
Capable|~할 수 있는, 유능한
Capture|붙잡다, 포착하다"""

        try:
            # Claude API 호출
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 응답 파싱
            response_text = message.content[0].text
            lines = response_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if '|' in line:
                    results.append(line)
            
            print(f"✅ 배치 {batch_num} 완료 ({len(lines)}개 처리)")
            
        except Exception as e:
            print(f"❌ 배치 {batch_num} 오류: {e}")
            # 오류 발생 시 해당 배치의 단어들을 빈 뜻으로 추가
            for word in batch:
                results.append(f"{word}|[뜻 추가 필요]")
    
    # 결과 저장
    print(f"\n💾 결과 저장 중: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in results:
            f.write(f"{line}\n")
    
    print(f"✅ 완료! {len(results)}개 단어 처리됨")
    print(f"\n📁 최종 파일: {output_file}")
    print(f"\n다음 단계: daily_test.py로 매일 테스트 자동화!")


if __name__ == "__main__":
    # 설정
    input_file = "words_cleaned.txt"
    output_file = "vocabulary_complete.txt"
    
    # API 키 입력받기
    print("=" * 60)
    print("Claude API를 사용하여 단어에 한국어 뜻을 추가합니다.")
    print("=" * 60)
    
    api_key = input("\n🔑 Claude API Key를 입력하세요: ").strip()
    
    if not api_key:
        print("❌ API 키가 필요합니다!")
        exit(1)
    
    print("\n시작합니다...\n")
    add_meanings_to_words(input_file, output_file, api_key)
