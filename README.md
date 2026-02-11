# Attack Surface Diff

A minimal tool that detects changes in an organization's attack surface over time using tools such as amass, subfinder, nmap and httpx.

DISCLAIMER : Please only use this tool on IP / domains you own, or if you have authorization of the owner.


## Automation with cron

`attackdiff` is designed to be automation-friendly and can be safely run from cron.

### Example: daily scan at 02:00

0 2 * * * attackdiff scan --scanner nmap --targets 1.2.3.4 5.6.7.8 >> ~/attackdiff.log 2>&1

### Explanation

- `>> ~/attackdiff.log`  
  Appends program output to a log file in your home directory

- `2>&1`  
  Redirects errors (stderr) into the same log file

- Exit codes:
  - `0` → success
  - `1` → user error (bad arguments, refused prune)
  - `2` → runtime failure (scanner error, IO failure)

Cron relies on exit codes to detect failures.

## More Examples:
### Weekly diff against baseline (Sunday 03:00)
0 3 * * 0 attackdiff diff --since baseline >> ~/attackdiff.log 2>&1

### Daily prune: keep last 10 untagged snapshots and 7 days of history
30 2 * * * attackdiff prune --keep-last 10 --keep-days 7 >> ~/attackdiff.log 2>&1

### Weekly prune of a specific tag, keep last 3
0 4 * * 0 attackdiff prune --tag baseline --keep-last 3 >> ~/attackdiff.log 2>&1

### Dry-run prune report every day
0 1 * * * attackdiff prune --dry-run --keep-days 3 >> ~/attackdiff.log 2>&1
