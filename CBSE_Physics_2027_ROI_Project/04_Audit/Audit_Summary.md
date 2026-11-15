# Audit summary

| Audit | Location | Scope | Result |
|---|---|---|---|
| Input integrity | `07_Source_Archive/Metadata/input_hashes_sha256.txt` | 16 supplied files | All present, all byte-identical to first registration |
| Image accounting | `03_Research_Data/Image_Accounting_Register/` | 15 photographs | 15/15 registered; OCR rejected as evidence; quality flagged per page |
| Source register | `03_Research_Data/Source_Register/source_register.csv` | Every source used | Authority level and verification status recorded per source |
| Dataset build | `03_Research_Data/**/*.csv` | 8 evidence CSVs | Row counts and totals checked by the validator |
| Model | `03_Research_Data/Model_Outputs/` | 8 CSVs + metadata | Invariants (sums, ranks, monotonicity, ROI identity) and byte-for-byte reproducibility |
| Workbook | `02_Excel_Workbook/` | 26 sheets, 736 formulas | Compiled and evaluated; 9 live checks OK; no unbalanced parentheses; quoted sheet refs |
| Reports | `01_Final_Reports/` | PDF (28 pp), concise PDF, Markdown | Key values present and matched to CSVs; limitations stated |
| Application | `05_Diagnostic_Application/` | PWA build | 53 logic + 30 DOM assertions pass; static offline/manifest checks pass; no browser execution performed |
| Adversarial review | `04_Audit/Adversarial_Audit/Adversarial_Audit.md` | 16 challenges | 4 accepted and disclosed, 3 tested and low-risk, remainder bounded by disclosed assumptions |
| Validation suite | `04_Audit/Validation_Reports/` | 99 checks | See `validation_report.md`; WARN entries are unexecuted checks, not passes |

## Standing statement

The validator and these audits establish that the artefacts are internally consistent,
reproducible from the stated inputs, and honest about what they do not contain. They do **not**
establish that the ranking predicts the 2027 paper. Chapter-level marks are not published by
CBSE; the chapter split inside each official unit cell is an inference, and the largest single
uncertainty is the preparation-hour estimate.
