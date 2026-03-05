#!/usr/bin/env bash
# ============================================================
# Parallel monthly land-area-weighted global mean for CoLM flux outputs
# Files: Global_IGBP_JRA55_hist_YYYY-MM.nc
# Vars:  f_rnof (mandatory), f_rsur (optional), f_etr (optional)
# Period: 1996-2000
#
# Output: landmean_1996_2000.csv
#
# Parallelization:
#  - Prefer GNU parallel if available
#  - Otherwise use xargs -P
# ============================================================

set -euo pipefail

# ---------------- user settings ----------------
DATA_DIR="${DATA_DIR:-/tera11/zhwei/students/Baifan/cases/JRA55}"
OUT_CSV="${OUT_CSV:-/stu02/weizx24/projects/JRA3Qand55/landmean_1996_2000.csv}"

# number of parallel jobs (files in parallel)
JOBS="${JOBS:-$(nproc)}"

# compute optional variables (1=yes, 0=no)
DO_F_RSUR="${DO_F_RSUR:-1}"
DO_F_ETR="${DO_F_ETR:-1}"
# ------------------------------------------------

cd "$DATA_DIR"

# Collect files for 1996-2000
mapfile -t FILES < <(ls -1 Global_IGBP_JRA55_hist_{1996..2000}-{01..12}.nc 2>/dev/null || true)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "[ERROR] No files found in $DATA_DIR with pattern Global_IGBP_JRA55_hist_YYYY-MM.nc for 1996-2000."
  exit 1
fi

# Pick a reference file to compute landarea sum only once
REF_FILE="${FILES[0]}"

# Compute denominator once: sum(landarea) over space (force single value)
# Using timmean+seltimestep to be safe if time dimension exists.
DEN=$(cdo -L -outputf,%0.15g -fldsum -seltimestep,1 -timmean -selname,landarea "$REF_FILE" | tail -n 1 | tr -d '[:space:]')

# Basic sanity check
python - <<PY
den=float("$DEN")
assert den>0, "DEN must be > 0"
print(f"[INFO] landarea sum (DEN) = {den}")
PY

# Worker: compute one file -> one CSV line
compute_one () {
  local f="$1"
  local y m
  y=$(echo "$f" | sed -n 's/.*_hist_\([0-9]\{4\}\)-\([0-9]\{2\}\)\.nc/\1/p')
  m=$(echo "$f" | sed -n 's/.*_hist_\([0-9]\{4\}\)-\([0-9]\{2\}\)\.nc/\2/p')
  [[ -n "$y" && -n "$m" ]] || { echo "[WARN] cannot parse date from $f" >&2; return 0; }

  # numerator for f_rnof: sum( timmean(f_rnof) * landarea )
  local NUM_RNOF RNOF
  NUM_RNOF=$(cdo -L -outputf,%0.15g -fldsum -mul \
            -seltimestep,1 -timmean -selname,f_rnof "$f" \
            -seltimestep,1 -timmean -selname,landarea "$f" \
            | tail -n 1 | tr -d '[:space:]')

  RNOF=$(python - <<PY
num=float("$NUM_RNOF"); den=float("$DEN")
print(num/den)
PY
)

  local line="${y}-${m},${RNOF}"

  if [[ "${DO_F_RSUR}" -eq 1 ]]; then
    local NUM_RSUR RSUR
    NUM_RSUR=$(cdo -L -outputf,%0.15g -fldsum -mul \
              -seltimestep,1 -timmean -selname,f_rsur "$f" \
              -seltimestep,1 -timmean -selname,landarea "$f" \
              | tail -n 1 | tr -d '[:space:]')
    RSUR=$(python - <<PY
num=float("$NUM_RSUR"); den=float("$DEN")
print(num/den)
PY
)
    line="${line},${RSUR}"
  fi

  if [[ "${DO_F_ETR}" -eq 1 ]]; then
    local NUM_ETR ETR
    NUM_ETR=$(cdo -L -outputf,%0.15g -fldsum -mul \
             -seltimestep,1 -timmean -selname,f_etr "$f" \
             -seltimestep,1 -timmean -selname,landarea "$f" \
             | tail -n 1 | tr -d '[:space:]')
    ETR=$(python - <<PY
num=float("$NUM_ETR"); den=float("$DEN")
print(num/den)
PY
)
    line="${line},${ETR}"
  fi

  echo "$line"
}

export -f compute_one
export DEN DO_F_RSUR DO_F_ETR

# Prepare header
if [[ "${DO_F_RSUR}" -eq 1 && "${DO_F_ETR}" -eq 1 ]]; then
  HEADER="date,land_mean_f_rnof,land_mean_f_rsur,land_mean_f_etr"
elif [[ "${DO_F_RSUR}" -eq 1 ]]; then
  HEADER="date,land_mean_f_rnof,land_mean_f_rsur"
elif [[ "${DO_F_ETR}" -eq 1 ]]; then
  HEADER="date,land_mean_f_rnof,land_mean_f_etr"
else
  HEADER="date,land_mean_f_rnof"
fi

TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_OUT"' EXIT

echo "[INFO] Running parallel jobs = $JOBS"
echo "[INFO] Files = ${#FILES[@]}"

# Parallel execution
if command -v parallel >/dev/null 2>&1; then
  # GNU parallel
  printf "%s\n" "${FILES[@]}" | parallel -j "$JOBS" --no-notice compute_one {} >> "$TMP_OUT"
else
  # xargs fallback
  printf "%s\n" "${FILES[@]}" | xargs -I {} -P "$JOBS" bash -c 'compute_one "$@"' _ {} >> "$TMP_OUT"
fi

# Sort by date and write final CSV
{
  echo "$HEADER"
  sort "$TMP_OUT"
} > "$OUT_CSV"

echo "[DONE] Output written to: $DATA_DIR/$OUT_CSV"
