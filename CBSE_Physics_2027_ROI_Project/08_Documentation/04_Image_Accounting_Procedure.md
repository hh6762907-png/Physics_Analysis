# Image accounting: the fifteen photographs

## Why a register at all

The MTG pages are the only source of the ten-year historical evidence, and they are
photographs, not scans: skewed, unevenly lit, and in two different rotations. Every page was
therefore accounted for individually — 15 of 15, no page silently skipped, no value guessed.

## Procedure applied to every image

1. **Inventory.** Filename, size, pixel dimensions, SHA-256 recorded before any processing
   (`input_inventory.csv`, `input_hashes_sha256.txt`).
2. **Orientation.** Rotation determined by inspection of the rendered page, then the image was
   rotated so text reads left-to-right (image 01 needs 180°, images 02–15 need 270°).
3. **Cropping.** Region of interest cropped per page and rendered at high zoom for reading.
4. **Reading.** Values read visually from the crops. This is the evidence.
5. **OCR.** RapidOCR was run on all 15 pages as a cross-check only. It is rotation-sensitive on
   these phone photographs and produced tables with misaligned columns; its output is logged
   (`ocr_attempt_log.csv`) and **no OCR value is used as evidence**.
6. **Reconciliation.** Page totals were checked against the printed page total where one
   exists; the ten-year aggregate was checked against the sum of yearly counts.
7. **Quality flags.** Blur, glare, perspective and cut-off text flagged per page
   (`image_quality_flags.csv`) with the effect on confidence.
8. **Register row.** One row per image in `image_accounting_register.csv`: page role, what was
   extracted, rows captured, confidence, whether any value was estimated.

## Results

| Aspect | Result |
|---|---|
| Images registered | 15 of 15 |
| Pages carrying usable tabular data | 15 |
| Pages where a value had to be estimated from an ambiguous glyph | recorded individually; estimates are flagged, never silently applied |
| Images with OCR used as evidence | 0 |
| Images where a second visual pass changed a value | recorded in `mtg_page_notes.csv` |

## How the MTG evidence is treated differently from the official evidence

The photographs are **secondary** evidence: a commercial publisher's compilation of past
papers, whose inclusion rules (which sets, which years, how duplicates were handled) are not
visible to us. They are therefore weighted 0.75 in source quality, capped at 35% of exposure,
and never allowed to override the official unit constraint. MTG's numbers are also never
described as "predictions" in this project: they are observations about the past, presented as
observations.

## Failure modes this procedure is designed to catch

* a page omitted entirely (register count catches it);
* a column read one row out of alignment (page-total reconciliation catches it);
* a digit misread (second visual pass + aggregate reconciliation catch it);
* OCR hallucination (OCR is logged but never used);
* a photographed page that is a different edition than assumed (flagged as an open question in
  the limitations, because no edition/date page was captured).
