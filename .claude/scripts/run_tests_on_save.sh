#!/bin/bash
# PostToolUse hook: src/*.py 수정 시 unit test 자동 실행
FP=$(python -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")
if echo "$FP" | grep -qiE '[/\\]src[/\\].*\.py$'; then
  python -m pytest tests/unit/ -x -q --tb=short
fi