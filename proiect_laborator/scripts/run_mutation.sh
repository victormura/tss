#!/usr/bin/env bash
# Cerința 7 — rulează mutmut și cosmic-ray pe trei suite de teste:
#   functional = Cerința 1 (EP + BVA + CEG)
#   mcdc       = Cerința 4 (MC/DC)
#   combined   = Cerința 1 + Cerința 4
# Rezultatele brute se salvează în mutation_results/.
set -u
cd "$(dirname "$0")/.."
OUT=mutation_results
mkdir -p "$OUT"

suite_tests() {
  case "$1" in
    functional) echo "tests/test_ep.py tests/test_bva.py tests/test_ceg.py" ;;
    mcdc)       echo "tests/test_mcdc.py" ;;
    combined)   echo "tests/test_ep.py tests/test_bva.py tests/test_ceg.py tests/test_mcdc.py" ;;
  esac
}

for name in functional mcdc combined; do
  tests="$(suite_tests "$name")"
  echo "=== mutmut :: $name ==="
  rm -f .mutmut-cache
  mutmut run --paths-to-mutate=src/parking_gate.py \
    --runner "python3 -m pytest -x -q -p no:cacheprovider $tests" > /dev/null 2>&1
  mutmut results > "$OUT/mutmut_${name}.txt" 2>&1
  cat "$OUT/mutmut_${name}.txt"

  echo "=== cosmic-ray :: $name ==="
  cat > "$OUT/cr_${name}.toml" <<EOF
[cosmic-ray]
module-path = "src/parking_gate.py"
timeout = 30.0
excluded-modules = []
test-command = "python3 -m pytest -x -q -p no:cacheprovider $tests"

[cosmic-ray.distributor]
name = "local"
EOF
  rm -f "$OUT/cr_${name}.sqlite"
  cosmic-ray init "$OUT/cr_${name}.toml" "$OUT/cr_${name}.sqlite" > /dev/null
  cosmic-ray exec "$OUT/cr_${name}.toml" "$OUT/cr_${name}.sqlite" > /dev/null 2>&1
  cr-report --show-pending "$OUT/cr_${name}.sqlite" > "$OUT/cosmic_ray_${name}.txt" 2>&1
  tail -n 5 "$OUT/cosmic_ray_${name}.txt"
done
git checkout -- src/parking_gate.py 2>/dev/null || true
