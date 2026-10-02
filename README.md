# English vocabulary test automation

This Python workflow turns an English/Korean vocabulary file into a daily practice sheet and publishes it as a Notion child page. It automates the repeated task of selecting words, formatting recall questions and assembling an answer key. The repository demonstrates that pipeline; it does not establish improved learning outcomes, time savings or adoption by learners.

## What actually runs

1. Optional one-time preparation: [setup_vocabulary.py](setup_vocabulary.py) reads `words_cleaned.txt`, asks Anthropic Claude for Korean meanings in batches of 100, and writes `vocabulary_complete.txt` as `word|meaning` lines. A prepared vocabulary is already tracked, so this paid step is not required to try the daily path.
2. [daily_test.py](daily_test.py) filters nonempty vocabulary lines containing `|` and uses `random.sample` to choose up to 20 lines without replacement within that run. It splits each line at the first separator.
3. Claude receives those words and a Korean prompt requesting 20 recall questions (10 in each translation direction), 3–5 four-option questions, answers and a review list.
4. The returned text is split on line boundaries into nominally 1,800-character chunks and sent to Notion as paragraph blocks in a new child page titled with the local date. Markdown is text inside paragraphs, not converted into native Notion headings or lists.
5. If the Notion upload raises an exception, the generated text is saved to `test_YYYYMMDD.md`. A Claude generation failure occurs before this upload fallback and is not caught there. Repeated successful runs create separate pages; there is no deduplication.

Both Python scripts request `claude-sonnet-4-5-20250929`. The daily script reads `CLAUDE_API_KEY`, `NOTION_TOKEN` and `NOTION_PAGE_ID` through `python-dotenv`/environment variables, then prompts for missing values. The preparation script instead prompts directly for its Claude key; it does not load the daily configuration.

## Choice and tradeoffs

Random sampling is a small, stateless selection mechanism, not spaced repetition. It stores no answers, mastery score, last-seen date or due schedule. Words can recur across days, duplicate source lines can produce duplicate words, and a vocabulary with fewer than 20 eligible lines yields fewer words even though the prompt still requests 20 questions. These are consequences of the implementation, not evidence of the owner's reasons for choosing it.

Claude supplies translations and question wording without a deterministic validator; Notion supplies a reading destination without a scoring loop. This keeps the workflow compact but leaves correctness and review to a person. Review vocabulary meanings, coverage, ambiguous prompts, distractors and answer keys before studying or sharing a generated sheet. The current program uploads before human review; it has no approval gate.

## Evidence, handled failure and remaining limits

The tracked [sample test dated 2025-11-01](test_20251101.md) contains recall questions, five multiple-choice questions, answers and a vocabulary review list. It is an inspectable output artifact, not a token-usage record, a verified successful Notion upload or an independently graded quality evaluation. No live run was made for this documentation revision.

The code explicitly addresses Notion's text-size boundary by splitting long output into paragraphs, and preserves text locally when upload fails. This documents a failure-handling mechanism, not a proven incident chronology. One unresolved edge case is concrete: a single line longer than the target is not subdivided and can still exceed the intended size limit. Large outputs also lack request batching or retry logic.

The preparation script preserves failed batches as `[뜻 추가 필요]` (“meaning needed”) entries; it does not verify that successful responses contain exactly one correct translation for every input word. The daily selector does not exclude those placeholders. Human review is therefore needed even before question generation. The old setup instructions named `clean_words.py`, `combined.txt` and `.env.example`, but these files are not tracked here; the instructions below use the available entrypoints instead.

## Setup on macOS / a Python terminal

Use a supported Python version compatible with the dependencies in [requirements.txt](requirements.txt); those dependencies have lower bounds rather than a lockfile. Place the checkout at `~/vocab-test` if you want to use the existing shell wrapper unchanged. Otherwise run directly from your checkout root.

```bash
cd /path/to/English-test---auto
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

For authorized live use, create your own local `.env` file (no template file is supplied) with these names and replace the placeholders locally:

```dotenv
CLAUDE_API_KEY=<your-anthropic-api-key>
NOTION_TOKEN=<your-notion-integration-token>
NOTION_PAGE_ID=<your-authorized-parent-page-id>
```

Obtain a Claude key from the [Anthropic console](https://console.anthropic.com/) and a Notion integration from [Notion integrations](https://www.notion.so/my-integrations). Connect that integration to the intended parent page and give it the necessary permission to create content. Never commit credentials, page identifiers or private generated content. Missing-value prompts use ordinary `input`, so unattended runs need configuration and interactive key entry may be visible on screen.

### One-time preparation (optional; paid API calls and local overwrite)

Review the supplied vocabulary first. If you deliberately want to regenerate meanings, `python3 setup_vocabulary.py` reads `words_cleaned.txt`, asks for the Claude key, calls the provider, and overwrites `vocabulary_complete.txt`. Back up your own curated vocabulary before doing this. There is no tracked cleaning script to run beforehand.

### Daily run (paid API call and external write)

```bash
# Run from the checkout root with the virtual environment active.
python3 daily_test.py
```

This calls Claude and creates a Notion page; it is not an offline smoke test. Selected words and a resulting page URL may appear in terminal output. Keep any logs private.

### Optional scheduling

[run_daily_test.sh](run_daily_test.sh) changes directory to `~/vocab-test`, activates `venv/bin/activate`, then runs `python3 daily_test.py`. It only works unchanged if that directory and virtual environment exist. After a deliberate manual live check, it can be invoked with `bash ~/vocab-test/run_daily_test.sh`; an optional cron entry for 09:00 in the host's timezone is:

```cron
0 9 * * * /bin/bash "$HOME/vocab-test/run_daily_test.sh"
```

Scheduling does not guarantee execution while a Mac is asleep or offline. Configure all three variables beforehand so the scheduled process does not wait for interactive input. Any output capture should be private and outside version control.

## Offline verification and troubleshooting

This check compiles source in memory without importing providers, loading local configuration, writing bytecode or making requests:

```bash
python3 -B -c 'from pathlib import Path; files=("daily_test.py", "setup_vocabulary.py"); [compile(Path(f).read_text(encoding="utf-8"), f, "exec") for f in files]; print("Syntax OK")'
bash -n run_daily_test.sh
```

Offline checks for this revision also exercised only the selector and chunker function definitions with a synthetic vocabulary and the tracked sample. They do not verify provider authentication, model availability, Notion permissions or live rendering. There is no tracked automated test suite.

For missing packages, activate the intended virtual environment and install the manifest. For wrapper failures, check the hard-coded directory and virtual environment path. For Notion errors, check the integration connection, parent page ID, permissions and block sizes; look for the local fallback file. For Claude errors, check the key, model availability, provider limits and [billing configuration](https://console.anthropic.com/settings/billing). Do not share tokens or private logs when requesting help.

## Cost boundary

No measured dollar estimate is provided. Preparation makes one request per batch of up to 100 input words with `max_tokens=4000`; a daily generation uses `max_tokens=8000`. These are output-token ceilings per request, not expected token counts or spending caps. Actual charges depend on input/output usage, current model pricing, frequency and repeated runs. The scripts do not record usage, enforce a budget or implement a local retry policy; provider SDK behavior may add retries. Check current pricing and account-level limits before live use, then record usage from an authorized run before estimating daily or monthly cost.

## Proposed next evaluation

Before adding a review schedule or claiming educational benefit, evaluate a fixed, human-reviewed vocabulary sample: retain the selected words and generated sheets, grade translation accuracy, coverage, answer-key agreement and distractor ambiguity, and report rejection/edit rates. Test malformed vocabulary, missing meanings, fewer-than-20 inputs, oversized single lines and simulated provider/upload failures offline. Define criteria before evaluating outputs. Any subsequent comparison of random sampling with spaced repetition needs an explicit learner-consent and outcome-measurement protocol; it is not an implemented feature here.