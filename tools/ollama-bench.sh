#!/usr/bin/env bash
# ollama-bench.sh - quick speed test for Ollama models
# Usage: ./ollama-bench.sh            # test every installed model (ollama list)
#        ./ollama-bench.sh --loaded   # only models currently in memory (ollama ps)
#        ./ollama-bench.sh qwen3.6:35b gemma4   # test named models
# Needs: curl, jq. Set OLLAMA_HOST to test a remote box (e.g. http://bc250:11434).
set -euo pipefail
HOST="${OLLAMA_HOST:-http://localhost:11434}"
[[ "$HOST" != http* ]] && HOST="http://$HOST"
PROMPT="${PROMPT:-Write a 200-word explanation of how a VLAN isolates network traffic.}"
NUM_PREDICT="${NUM_PREDICT:-256}"

if [[ "${1:-}" == "--loaded" ]]; then
  mapfile -t MODELS < <(curl -s "$HOST/api/ps" | jq -r '.models[].name')
elif [[ $# -gt 0 ]]; then
  MODELS=("$@")
else
  mapfile -t MODELS < <(curl -s "$HOST/api/tags" | jq -r '.models[].name' | sort)
fi
[[ ${#MODELS[@]} -eq 0 ]] && { echo "No models found at $HOST"; exit 1; }

printf "%-55s %9s %10s %9s %8s\n" MODEL "LOAD s" "PROMPT t/s" "GEN t/s" "TOKENS"
for m in "${MODELS[@]}"; do
  r=$(curl -s "$HOST/api/generate" -d "$(jq -n --arg m "$m" --arg p "$PROMPT" --argjson n "$NUM_PREDICT" \
      '{model:$m, prompt:$p, stream:false, think:false, options:{num_predict:$n, temperature:0}}')")
  if [[ -z "$r" ]] || echo "$r" | jq -e '.error' >/dev/null 2>&1; then
    printf "%-55s  ERROR: %s\n" "$m" "$(echo "$r" | jq -r '.error // "no response"' 2>/dev/null)"; continue
  fi
  echo "$r" | jq -r --arg m "$m" '
    [ $m,
      ((.load_duration // 0) / 1e9),
      (if (.prompt_eval_duration // 0) > 0 then .prompt_eval_count / (.prompt_eval_duration / 1e9) else 0 end),
      (if (.eval_duration // 0) > 0 then .eval_count / (.eval_duration / 1e9) else 0 end),
      (.eval_count // 0) ] | @tsv' |
    awk -F'\t' '{printf "%-55s %9.1f %10.1f %9.1f %8d\n", $1, $2, $3, $4, $5}'
done
echo
echo "Check GPU vs CPU split with: ollama ps"
