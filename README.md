# gramide-json

An independent `gramide_json` package with an original scanner and grammar
written against [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259).

`check` validates JSON syntax: scalar or structured top-level values, objects,
arrays, strict numbers, JSON escapes and whitespace. Comments, trailing commas,
single quotes, unquoted keys, nonfinite numbers and additional documents fail.
As RFC 8259's grammar permits, duplicate object names and escaped unpaired
surrogates are accepted; this is syntax validation, not application data validation.
A leading BOM is rejected. Input uses gramide's existing UTF-8 text-file contract.

`parse` exposes objects, arrays and pairs. `outline`, `symbols`, `tags` and `map`
list object keys as properties. Names retain their source quotes and escapes;
the package does not invent a JSONPath or decode keys. All ranges are UTF-8 byte
ranges into the original source. No `symbols-recovered` capability is claimed.

From this directory: `almide test`, then
`almide build cli/main.almd -o gramide_json`.
Regenerate the committed table with `./gramide_json gen-table > src/table.almd`.
Repository CI includes lexical/grammar negatives and a Python JSON oracle gate.

MIT or Apache-2.0, at your option; see LICENSE-MIT and LICENSE-APACHE.

## Repository contract

This repository owns this language package and its tests. `src/mod.almd` exports
`definition()` using the shared gramide package API. The `gramide-cli` repository
composes it as a git dependency; no grammar source is vendored into the CLI.
`bash ci/check.sh` runs the complete package gate with an explicit test entry
point, avoiding recursive parallel compiler fan-out. CI pins Almide and Rust
in `.github/workflows/quality.yml`.
