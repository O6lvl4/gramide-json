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

## Incremental boundaries

Object members and array values are incremental items. Edits inside a key or
string can reuse the surrounding tree without re-lexing the entire document.
`src/incremental_test.almd` checks local item reuse, committed-table parity,
exact fresh-tree equality, source positions and node-ID retention. Strict JSON
acceptance is unchanged: missing values, extra documents and trailing commas
remain errors. Damaged-document recovery is still a separate, limited reader
behavior, and no recovered-symbol capability is advertised.

The incremental item boundaries require the parent-window safeguards in
[gramide #87](https://github.com/O6lvl4/gramide/pull/87). This draft pins that
core development branch to commit `4916bbdce30bd2814429e69a98450faf8c02e1b8`
in `almide.lock`. It does not claim that the released v0.2.11 core includes
these fixes; replace the development pin with the next core release after merge.

## Missing-closer recovery

Container members use bounded recovery and a comma, their own closing delimiter,
or actual EOF as their non-consuming boundary. This preserves complete members
when an outer closer is missing; the strict grammar still requires each closer.
The ordinary `lang.read_lang` API reports invalidity and unpaired token indices
even when the recovered tree has no `ERROR` nodes. A recovered tree is not proof
that JSON is valid or that every malformed input retains useful structure.

`src/recovery_test.almd` covers missing array/object closers, complete empty
containers, nested missing closers, UTF-8 byte coordinates, CRLF, strict rejection,
diagnostics and gaps, and ordinary-reader/direct-recovery parity. The complete
serial package test root is `src/package_test.almd`; run `bash ci/check.sh` for
those tests plus the existing CLI, generated-table and Python oracle gates.
No additional core API or dependency pin is required. Root-prefix recovery
remains unsupported.
