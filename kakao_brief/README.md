# kakao_brief — 나스닥 모닝 브리핑 카드 → 카카오톡 나에게 보내기

코드만으로 동작(컴퓨터 유즈·LLM 호출 없음). 카드 3장(지수 / 섹터 / 매크로)을 만들어 카카오 "나에게 보내기"로 발송.

```
python main.py --sample --out cards   # 오프라인 미리보기 (가짜 데이터)
python main.py --dry-run              # 실제 시세로 카드만 생성
python main.py                        # 카드 생성 + 카카오 발송
```

## 1회 설정
1. developers.kakao.com 앱 생성 → [카카오 로그인] 활성화, Redirect URI 등록, 동의항목 `talk_message`(카카오톡 메시지 전송) 설정.
2. [제품 링크 관리]에 웹 도메인 등록 (메시지 링크용, 값은 저장소 변수 `KAKAO_LINK_URL`).
3. `python kakao_auth.py <REST키> <RedirectURI>` → URL 접속·동의 → 주소창의 `code=` 값으로 다시 실행 → 리프레시 토큰 출력.
4. GitHub 저장소 Secrets: `KAKAO_REST_API_KEY`, `KAKAO_REFRESH_TOKEN` (클라이언트 시크릿을 켰다면 `KAKAO_CLIENT_SECRET`).
5. Actions → morning-brief → Run workflow (dry_run 해제)로 1회 테스트.

## 알아둘 점
- 스케줄은 화~토 07:00 KST(cron `0 22 * * 1-5` UTC). GitHub cron은 수 분 지연될 수 있음.
- 리프레시 토큰은 유효기간이 있어(약 2개월) 갱신 응답에 새 토큰이 오면 로그에 안내가 뜸 → 시크릿 교체 필요.
- 시세는 Yahoo 비공식 chart 엔드포인트. 뉴스·공포탐욕지수는 아직 미포함(LLM 없이 넣으려면 RSS 제목만 사용).
- 폰트: Actions에서는 `fonts-noto-cjk` 설치, 로컬은 `BRIEF_FONT_DIR` 또는 `kakao_brief/fonts/` 사용.
