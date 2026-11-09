# LOGIC-EXEC-V2 — 4B diagnostic evidence reconciliation

Date: 2026-11-07
Status: INCOMPLETE / ORIGINAL BALLOT TRACES NOT RECOVERED
Classification: read-only evidence reconciliation, not Executive qualification

## Source and identity

Central Control issue #149 records a chair-reported isolated 4B diagnostic with four accepted AIR_002–005 and four rejected AIR_001, AIR_006–008; it references commit `6aa44d6`. The report is a secondary outcome summary, not the raw eight-ballot evidence.

The commit resolves to `6aa44d6b4200e467d246668bdc9b980ce2cad69c`, dated 2026-11-05, with message `fix(exec): preserve decision transcript artifact on failed qualification`. It modifies the workflow artifact-upload step.

## Independently inspected GitHub Actions evidence

Run: https://github.com/extraheathliberty/XYRA_CENTRAL_CONTROL/actions/runs/42046895722

- Event: push; head SHA: `6aa44d6b4200e467d246668bdc9b980ce2cad69c`
- Workflow conclusion: FAILURE.
- Job `executive-table`, job ID `127312186464`: FAILURE.
- `Install and start Ollama`: FAILURE; HTTP 404 during download, followed by gzip/tar errors and exit code 2.
- `Pull Executive model`: SKIPPED.
- `Run eight-Executive decision`: SKIPPED.
- `Upload decision transcript`: step SUCCESS, but logs say no file at `executive_live_decision.log`.
- Artifact listing for run: EMPTY.

**Disposition:** this workflow contains zero executed deliberations and no recovered raw ballots. It does not prove or disprove the separate reported local diagnostic. Do not label the 4/8 local report independently verified on the basis of this commit or workflow.

## Other preserved history

CC #159 records:
- Run 42040644537: fail at AIR_001, zero valid votes, criterion double classification of 8B/14B comparison.
- Run 42043815104: AIR_001–003 validated, AIR_004 failed on production-admission double classification; three valid votes, not eight.
- Earlier 41863953657: workflow SUCCESS despite VotingContractError; false-green execution control defect.

These are distinct executions and may not be pooled into a single eight-Executive vote.

## Remaining evidence gates

1. Locate the local diagnostic's exact run identity, execution timestamp, command, model digest and environment.
2. Preserve raw prompts, responses, ballot validation records, signatures/nonce references, and failure codes for each AIR.
3. Hash and freeze originals; establish provenance from each ballot to its run and source commit.
4. Replay each original ballot against the actual Logic Lab validator and compare exact expected/observed classification.
5. Independent reviewer to reproduce without changing original artifacts.
6. Only then update per-AIR qualification, with no inference of institutional adoption, live process admission or security-hold release.

SEC-01/C1 remains ACTIVE. No model execution or agent activation authorized by this evidence note.
