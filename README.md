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

The incremental item boundaries use the parent-window and identity safeguards
merged in [gramide #87](https://github.com/O6lvl4/gramide/pull/87). The optional
paired-head reader additionally requires the paired v2 APIs introduced in
[gramide #88](https://github.com/O6lvl4/gramide/pull/88) and current-state recovery
trials from the selected core revision. The compatibility version alone does
not identify those capabilities: use the exact Git dependency and lockfile,
and rerun dependency integration when selecting a containing core revision.

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
These existing checks continue to exercise `definition()` and its default
table. Root-prefix recovery remains unsupported by that default Definition.

## Optional paired-head reader

`recovery_definition()` is the supported opt-in entry point for richer ordinary
recovery. Its `islands_grammar.almd` blueprint composes the retained
`recovery_grammar.almd` rules and supplies the generated v2 `recovery_table.almd`.
`definition()`, the default grammar/table, scanner and CLI registration keep
their existing behavior. Strict JSON acceptance and valid-input named trees and
token coordinates are unchanged. Malformed recovery output, recovery-site
indices, names-arena indices and fresh-constructor numbering can change.

Use `lang.compile(gramide_json.recovery_definition())` with the normal
`lang.read_lang` API. Preserve strict validity from `Reading.error`: a recovered
tree with zero ERROR nodes can still represent invalid JSON. No recovered-symbol
capability or Prepared certification is added.

The two trailing-comma heads and the root object punctuation-gap head require
the actual consumed closer to be mutually paired with the head's original
opener. A closer belonging to an inner
container cannot close an outer head: the direct outer head on `[[1,]` is
refused and its output is rolled back. This proves outer delimiter ownership;
recovering trailing-head interiors can still contain genuine ERROR children.

The added root object head accepts exactly one missing comma between complete
pairs, or one missing colon before a complete value. Its value graph contains
no recovery operators and consumes real paired closers. Extra punctuation
omissions, malformed lexical tokens and incomplete nested values are refused.
A separate document-prefix head preserves consecutive complete values while
leaving the final value for the normal resume path; it requires real progress
and rolls back a value that ends at EOF. These are bounded recovery envelopes,
not relaxed strict JSON syntax.

The current runtime blueprint is `islands_grammar.rules()!`. Compile it with
`parser.compile_with_paired_heads` and all three names from
`islands_grammar.selected_heads()`: `"pair_gap_object_head"`,
`"trailing_array_head"` and `"trailing_object_head"`. The convenience
`islands_grammar.compiled()!` applies those annotations. The unwrapped
`document_prefix_head` is not a paired container head.

The retained `recovery_grammar.rules()` is the earlier foundation and omits the
new root envelopes; it is no longer interchangeable with the richer public table.
Plain `parser.compile` also omits the paired ownership annotations.
Runtime/table parity means annotated compilation against the v2 table. Old cores
reject generated v2 source at the missing `from_tables_v2` loader; there is no
automatic downgrade. Raw integer-table transports need an external format-2
capability envelope.

Regenerate this opt-in table by building `ci/recovery_table.almd` and redirecting
that executable's stdout to `src/recovery_table.almd`. The CLI's `gen-table`
command continues to generate only the default `src/table.almd`.

### Incremental identity and fallback

The opt-in grammar adds a root RecoverAll Item and nonempty recovery heads.
Item layout, recovery sites, names-arena indices and fresh-constructor numbering
can differ from `definition()` and earlier recovery definitions. Keep one
Definition and core revision throughout an incremental history;
IDs from independently constructed default and opt-in documents are not a shared
identity domain. Within the chosen Definition, the generic edit checks require
unaffected node IDs to survive, changed ancestor nodes to receive fresh IDs, no retired
ID reuse, valid counters, and exact fresh-reader materialization.

A non-DONE `incremental.reparse_status` result requests a whole-file fallback and
may append diagnostics to `Document.trace`. The caller may consume those
messages. That raw call does not establish full-Document transactionality or a
new Prepared guarantee. The bounded generic tests check that every other Document field, including
nested Item traces, Compiled, source/provenance and counters, stays exact on
fallback requests, and that the existing Document.trace prefix is preserved.

### Bounded retention and remaining limits

The root envelopes retain the complete records in these three formerly losing
witnesses, while strict parsing still rejects each document:

- A pair with a container value before a missing comma: `{"a":{"x":1} "b":2}`
- A missing colon before a container value: `{"a" [1,{"b":2}],"c":3}`
- Three consecutive documents: `[1] {"k":2} true`

The missing-comma and missing-colon witnesses retain 9 and 10 complete records,
respectively; the three-document witness retains all 7. `Reading.error` remains
set even when recovery emits no ERROR nodes. Raw incremental DONE is likewise
not a strict-validity certificate.

This does not promise lossless recovery for arbitrary damage. Multiple missing
punctuation marks, lexical damage, incomplete or mismatched nested containers,
and damaged non-root envelopes remain outside these new strict-interior heads.
The older fallback and trailing heads may still retain partial nodes or ERROR
children. Paired ownership alone does not certify every recovered interior, and
no Prepared certificate or recovered-symbol capability is provided. Correctness
validation makes no speed, allocation or memory claim.

### Maintained checks

The explicit `src/package_test.almd` root imports the original incremental and
recovery tests plus `paired_recovery_test.almd` and `islands_test.almd`. All 29
package-owned tests are reachable, including scanner/strict-grammar tests. Core tests are
also run; their count can change with the dependency. `ci/check.sh` checks that
root, executes it, and byte-compares both default and v2 generated tables before
running the existing CLI/fixture/Python oracle gates. The GitHub Quality workflow
calls that script, so the new tests and generation parity run in maintained CI.

The separate fixed integration protocol covers 56 fresh inputs, 396 direct-head
rows across runtime/table readers, 448 default-reader pairs and 370 revision
snapshots per reader (740 total). It retains full trees including malformed
containers, actual strict invalidity, source/field/site spans, ID/counter rules
and fallback traces. It uses the unchanged public 320 edits plus 39 explicitly
documented malformed edits. Results must be tied to the exact package, core and
generated bytes; they do not replace maintained CI or establish unbounded editing
guarantees. Older 301/45/26/332 artifacts are unavailable and are not part of the
current gate.
