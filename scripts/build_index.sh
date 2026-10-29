#!/usr/bin/env bash
# Build a page-preserving text index from the local official PDF collections.
# MANUAL_PDF_DIR and MANUAL_TEXT_DIR may override the skill-local defaults.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
TASK_RELEASE="${STRELEASE:-W-2024.09-SP1}"
PDFROOT="${MANUAL_PDF_DIR:-$SKILL_DIR/references/manuals}"
OUT="${MANUAL_TEXT_DIR:-$SKILL_DIR/references/manual_index/$TASK_RELEASE/text}"
PDFROOT="${PDFROOT%/}"

command -v pdftotext >/dev/null || {
  echo "pdftotext not found; install Poppler before building the index" >&2
  exit 1
}
command -v find >/dev/null || { echo "find not found" >&2; exit 1; }
command -v sort >/dev/null || { echo "sort not found" >&2; exit 1; }

if command -v sha256sum >/dev/null; then
  HASHER=sha256sum
elif command -v shasum >/dev/null; then
  HASHER=shasum
elif command -v openssl >/dev/null; then
  HASHER=openssl
else
  echo "SHA-256 tool not found; need sha256sum, shasum, or openssl" >&2
  exit 1
fi

sha256_file() {
  local path="$1"
  local output
  case "$HASHER" in
    sha256sum)
      output="$(sha256sum -- "$path")"
      printf '%s\n' "${output%% *}"
      ;;
    shasum)
      output="$(shasum -a 256 "$path")"
      printf '%s\n' "${output%% *}"
      ;;
    openssl)
      output="$(openssl dgst -sha256 "$path")"
      printf '%s\n' "${output##* }"
      ;;
  esac
}

[[ -d "$PDFROOT" ]] || {
  echo "PDF root not found: $PDFROOT" >&2
  exit 1
}

mapfile -d '' -t pdfs < <(
  find "$PDFROOT" -type f -iname '*.pdf' -print0 | LC_ALL=C sort -z
)
(( ${#pdfs[@]} > 0 )) || {
  echo "No PDFs found recursively under: $PDFROOT" >&2
  exit 1
}

mkdir -p "$OUT"
manifest_tmp="$OUT/.sources.tsv.tmp.$$"
task_tmp=""
cleanup() {
  [[ -z "$task_tmp" ]] || rm -f -- "$task_tmp"
  rm -f -- "$manifest_tmp"
}
trap cleanup EXIT
printf 'index_file\tsha256\tstatus\tsource_pdf\n' > "$manifest_tmp"

declare -A digest_to_index=()
declare -A index_to_digest=()
unique=0
duplicates=0
converted=0
skipped=0

for pdf in "${pdfs[@]}"; do
  rel="${pdf#"$PDFROOT"/}"
  filename="${pdf##*/}"
  base="${filename%.*}"
  digest="$(sha256_file "$pdf")"

  if [[ -n "${digest_to_index[$digest]+x}" ]]; then
    index_name="${digest_to_index[$digest]}"
    printf 'duplicate %s -> %s\n' "$rel" "$index_name"
    printf '%s\t%s\tduplicate\t%s\n' \
      "$index_name" "$digest" "$rel" >> "$manifest_tmp"
    ((duplicates += 1))
    continue
  fi

  index_name="$base.txt"
  if [[ -n "${index_to_digest[$index_name]+x}" && "${index_to_digest[$index_name]}" != "$digest" ]]; then
    index_name="${base}__${digest:0:12}.txt"
  fi
  digest_to_index[$digest]="$index_name"
  index_to_digest[$index_name]="$digest"
  ((unique += 1))

  target="$OUT/$index_name"
  printf '%s\t%s\tprimary\t%s\n' \
    "$index_name" "$digest" "$rel" >> "$manifest_tmp"

  if [[ -s "$target" && "$target" -nt "$pdf" ]]; then
    echo "skip $index_name (index newer than PDF)"
    ((skipped += 1))
    continue
  fi

  task_tmp="$target.tmp.$$"
  if ! pdftotext -layout "$pdf" "$task_tmp"; then
    echo "Conversion failed: $pdf" >&2
    exit 1
  fi
  mv -f -- "$task_tmp" "$target"
  task_tmp=""
  echo "converted $rel -> $index_name"
  ((converted += 1))
done

mv -f -- "$manifest_tmp" "$OUT/_sources.tsv"
trap - EXIT
echo "BUILD_DONE release=$TASK_RELEASE inputs=${#pdfs[@]} unique=$unique duplicates=$duplicates converted=$converted skipped=$skipped output=$OUT"
