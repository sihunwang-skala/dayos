# DayOS 저장공간 정책

> 최종 확인: 2026-10-31 · 대상: 개발자 Mac (Apple M2 Pro, 32GB, macOS 26.3.1)

## 1. 원칙

| 위치 | 저장 대상 |
|---|---|
| **Mac 로컬 + GitHub** | 소스코드, 설정, 명세(`docs/`), 다운로드/평가 스크립트, 모델·데이터 메타데이터(`registry/`), Git 이력 |
| **외장하드 (`$DAYOS_ASSETS_ROOT`)** | LLM 가중치, HF/torch/pip 캐시, 대용량 데이터셋, Fine-tuning 결과물, Checkpoint, 대용량 평가 결과, 추론용 대용량 임시 파일 |

- GitHub에는 모델 가중치·데이터 원본을 **절대 Commit하지 않는다** (`.gitignore`로 차단).
- 외장하드가 연결·검증되지 않으면 **모든 다운로드는 중단**된다. 내부 디스크로 자동 대체(fallback)하지 않는다.
- 외장하드 경로는 **추측하지 않는다.** `setup-external-storage.sh`가 실제 Mount 정보를 보여주고 사용자 승인 후에만 기록한다.
- 환경변수는 **프로젝트 스크립트 내부에서만** 설정한다. `~/.zshrc`, `launchctl setenv` 등 전역 설정은 변경하지 않는다.

## 2. 현재 Mac 상태 (2026-10-31 조사)

| 항목 | 값 |
|---|---|
| 내부 디스크 | APFS 460GiB, **여유 약 33GiB (93% 사용)** |
| 외장하드 | **미연결** (`/Volumes`에 `Macintosh HD`만 존재) |
| Python | 3.11.15 (Homebrew), uv 0.11.29 |
| huggingface_hub / `hf` CLI | 1.32.0 (`huggingface-cli`는 deprecated) |
| Ollama | 0.33.0 (서버 미실행) |
| torch | 미설치 |
| git-lfs | 미설치 (필요 없음 — HF는 `huggingface_hub`로 받음) |
| 기존 내부 캐시 | `~/.cache/huggingface` **26GB**, `~/.ollama` **23GB** (다른 프로젝트 소유, DayOS 스크립트는 건드리지 않음) |

> 내부 여유공간이 33GB뿐이므로, 7B BF16 모델(14.5GB) 하나만 내부에 받아도 여유가 절반으로 줄어든다. 외장하드 연결 전 다운로드 금지 정책의 직접적인 이유다.
> 기존 내부 캐시(약 49GB)의 정리·이전 여부는 해당 프로젝트 소유자가 별도로 결정한다.

## 3. 외장하드 디렉터리 구조

```
$DAYOS_ASSETS_ROOT/              # 예: /Volumes/<드라이브명>/dayos-assets  (실제 경로는 연결 후 확인)
├── .dayos-assets                # 마커 (Volume UUID). 없거나 불일치하면 스크립트 중단
├── models/
│   ├── skt/<모델명>/<revision 12자>/   # 공식 SKT 가중치 (snapshot_download local_dir)
│   ├── other/                   # 커뮤니티 양자화(GGUF 등), 타사 모델
│   └── ollama/                  # OLLAMA_MODELS
├── datasets/
│   ├── raw/<dataset>/<sample|full>/
│   └── processed/
├── cache/
│   ├── huggingface/{hub,xet,assets}   # HF_HOME, HF_HUB_CACHE, HF_XET_CACHE, HF_ASSETS_CACHE
│   ├── transformers/            # (예약) transformers v5는 HF_HUB_CACHE 사용
│   ├── torch/                   # TORCH_HOME
│   ├── pip/  uv/  xdg/          # PIP_CACHE_DIR, UV_CACHE_DIR, XDG_CACHE_HOME
├── tmp/                         # TMPDIR (다운로드 임시파일)
├── checkpoints/
├── experiments/
├── logs/
└── manifests/                   # 다운로드별 검증 결과 JSON
```

## 4. 환경변수 (검증된 것만)

`scripts/lib/storage-env.sh`(셸)와 `scripts/dayos_storage.py`(Python)가 같은 값을 설정한다.

| 변수 | 대상 | 검증 |
|---|---|---|
| `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, `HF_ASSETS_CACHE` | huggingface_hub / transformers / datasets | huggingface_hub 1.32.0 `constants.py`에서 확인 |
| `HF_TOKEN_PATH` | HF 로그인 토큰 | 1.32.0 지원. 토큰은 Mac(`~/.cache/huggingface/token`)에 그대로 둔다 |
| `TORCH_HOME` | torch hub | torch 미설치 — 설치 시 재확인 필요 |
| `XDG_CACHE_HOME` | 기타 XDG 준수 도구 | 스크립트 실행 셸에서만 |
| `PIP_CACHE_DIR`, `UV_CACHE_DIR` | pip / uv | pip 26.2, uv 0.11.29 지원 |
| `OLLAMA_MODELS` | Ollama 모델 | `ollama serve --help`(0.33.0)에서 확인. **서버 프로세스가 읽는 값**이므로 `source scripts/dayos-env.sh && ollama serve`로 실행해야 한다. Homebrew 서비스(`brew services`)로 띄운 서버에는 적용되지 않는다 |
| `TMPDIR` | Python `tempfile`, 대부분의 CLI | 스크립트 실행 중에만 |

수동 터미널 작업(예: Ollama, Jupyter)은 `source scripts/dayos-env.sh` 후 실행한다. 외장하드가 준비되지 않으면 이 스크립트는 환경을 바꾸지 않고 실패한다.

## 5. 안전장치

1. `DAYOS_ASSETS_ROOT`는 `/Volumes/<드라이브>/` 아래여야 함
2. 해당 볼륨이 실제 Mount Point여야 함 (`/Volumes` 아래 일반 폴더 → 거부)
3. `$HOME`과 다른 장치여야 함 (`st_dev` 비교)
4. 마커 파일 존재 + Volume UUID 일치 (다른 드라이브를 같은 이름으로 꽂은 경우 차단)
5. 쓰기 권한
6. 여유공간 ≥ 다운로드 크기 × 1.1 + 5GB
7. 100GB 초과 또는 `blocked-large` 모델은 `--allow-large` 없이는 실행 불가
8. 다운로드 후 파일 크기·LFS SHA-256 검증, `~/.cache/huggingface` 증가량 감시

파일시스템: **APFS 권장**. exFAT은 동작하나 심볼릭 링크가 없어 HF 캐시가 복사 방식으로 동작하고 `._*` 파일이 생긴다. FAT32는 4GB 초과 파일 불가 → 설정 스크립트가 거부.

## 6. 내부 저장공간 사용을 0으로 만들 수는 없다

외장하드로 옮겨도 다음은 내부 디스크에 남는다.

- 소스코드, `.venv`, `node_modules`, Git 객체
- macOS 시스템 캐시·스왑(`/private/var/vm`) — 대형 모델 추론 시 메모리 압박으로 스왑이 수 GB 늘 수 있음
- Spotlight 인덱스 (외장하드는 `mdutil -i off`로 끌 수 있으나 시스템 설정 변경이므로 사용자가 직접 결정)
- `TMPDIR`을 무시하고 `/tmp` 또는 `~/Library/Caches`에 쓰는 도구
- HF 토큰 등 소형 설정 파일
- 모델을 메모리에 올릴 때의 mmap은 디스크를 쓰지 않지만, 외장하드가 느리면 로딩이 느려진다 (USB 3.2/Thunderbolt SSD 권장)

## 7. 작업 순서

```bash
scripts/setup-external-storage.sh                    # 연결된 볼륨 목록만 출력
scripts/setup-external-storage.sh --volume /Volumes/<NAME> --dry-run
scripts/setup-external-storage.sh --volume /Volumes/<NAME>   # 보고서 확인 후 y
scripts/check-storage.sh
python3 scripts/download-model.py --list
python3 scripts/download-model.py ax-4.0-light --dry-run     # 크기·메모리 보고 → 사용자 승인
```
