# Florida Homes Held in Trust, by County (2026)

How many Florida homes are owned by a trust, county by county, read from the 2026 Florida Department of Revenue property roll. For each of Florida's 67 counties the dataset counts the parcels whose recorded owner is a trust or a trustee, how many of them are residential, how many carry a homestead exemption, what the owner name says about the kind of trust (revocable, irrevocable, testamentary or land trust), and whether one trustee or several are named. Land trusts are counted separately from family trusts, and banks, companies and public bodies acting as trustee are excluded.

Compiled by [Kevin D. Klagge, Esq.](https://stepuplaw.com/about), a Florida estate planning attorney (Klagge Law, PLLC). Built on September 30, 2026. The data holds counts and dollar totals only. No owner name, address or parcel number is published.

- Canonical page with the county table and the citation: <https://stepuplaw.com/data/florida-homes-held-in-trust/>
- Source repository: <https://github.com/stepuplaw/florida-homes-in-trust-dataset>

## What the data shows

Across the state, 600,542 residential parcels are held in trust, which is 6.11% of Florida's 9,830,053 residential parcels, with a combined just (market) value of $347.5 billion on the roll. Of those, 582,392 are in a family trust (5.92% of residential parcels) and 18,150 are in a land trust. The six counties flagged below undercount trusts, so the true statewide share is somewhat higher. Across the other 61 counties, 6.26% of residential parcels are in a family trust.

270,615 trust parcels carry a homestead exemption, and 268,631 of them are in a family trust. A Florida homestead keeps its exemption in a revocable trust when the owner keeps the beneficial interest, so these are mostly people living in a home they have already placed in their own trust.

Counting every kind of property, 651,646 parcels are held in trust (5.88% of 11,090,196 parcels), with a just value of $374.5 billion. Another 4,911 parcels name a bank, company or public body as trustee and are excluded from every count.

| Share of residential parcels in a family trust | County |
|---|---|
| 19.15% | Collier |
| 13.16% | Sarasota |
| 12.15% | Lee |
| 12.09% | Indian River |
| 11.45% | Sumter |
| 9.31% | Charlotte |

Lee has the most homes in a family trust (64,041), followed by Miami-Dade (51,589), Collier (45,852), Sarasota (38,308) and Pinellas (34,740).

The owner name says what kind of trust it is only about a fifth of the time. Of the 651,646 trust parcels, 118,647 (18.2%) say revocable or living trust, 3,598 say irrevocable, 115 say testamentary, 20,880 are land trusts and 508,406 (78.0%) do not say.

`FINDINGS.md` has the full breakdown.

## Files

| Path | Contents |
|---|---|
| `data/trusts_by_county.csv` | One row per county (67 rows) |
| `data/trusts_statewide.json` | Statewide totals, with the breakdowns by kind, trustee count and land trust type for all parcels, residential parcels and homesteads |
| `data/schema.json` | Column dictionary as a Frictionless Table Schema |
| `data/datapackage.json` | Frictionless Data Package descriptor |
| `tools/trusts.py` | The script that built the files (see the note below) |
| `FINDINGS.md` | Headline numbers and county rankings |

`tools/trusts.py` is published so the method can be read and checked. It does not run on its own. It imports `classify.py` (the owner classifier) and `build.py` (the county list and number parsing) from the StepUp Law fl-owners project, and it reads the Department of Revenue NAL zip files, which are public but large. The owner-name samples it writes for quality review stay private and are not in this repository.

## Columns

| Column | Meaning |
|---|---|
| `county` | County name |
| `parcels` | All real property parcels on the county roll |
| `trust_parcels` | Parcels whose owner is a trust or trustee, institutions excluded, land trusts included |
| `pct_parcels_in_trust` | `trust_parcels` as a percentage of `parcels` |
| `trust_just_value` | Total just (market) value on the roll of `trust_parcels`, in dollars |
| `residential_parcels` | Parcels with a Department of Revenue residential use code (000 to 009 except 003), which covers vacant residential land, single family, mobile homes, condominiums, cooperatives, retirement homes, multifamily under 10 units and residential common elements |
| `trust_residential_parcels` | Residential parcels held in trust, land trusts included |
| `pct_residential_in_trust` | `trust_residential_parcels` as a percentage of `residential_parcels` |
| `trust_homestead_parcels` | Trust parcels with a homestead exemption value on the roll |
| `kind_revocable`, `kind_irrevocable`, `kind_testamentary`, `kind_land`, `kind_unstated` | Trust parcels by what the owner name says about the trust |
| `trustees_single`, `trustees_joint`, `trustees_trust_named` | One trustee named, two or more named, or the trust itself written as owner with no trustee word |
| `land_numbered`, `land_named`, `land_corporate_trustee` | Land trusts identified by a trust number, by the words "land trust", or by a title or land trust service company as trustee |
| `family_trust_parcels`, `family_trust_residential_parcels`, `family_trust_homestead_parcels` | The trust counts with land trusts taken out |
| `pct_residential_in_family_trust` | `family_trust_residential_parcels` as a percentage of `residential_parcels` |
| `homestead_on_roll` | `floor` where a county with 10,000 or more homes in a family trust shows a homestead exemption on under 20% of them (Broward, Palm Beach), a recording difference; `recorded` otherwise |
| `trust_designation_on_roll` | `recorded`, or `unreliable` where the county roll writes owner names without the trustee designation (see Limits) |

## Method

The source is the Name-Address-Legal (NAL) real property file the Florida Department of Revenue publishes for each county. The 2026 files are the preliminary roll for 66 counties and the final roll for Citrus County.

Every parcel is first sorted by an owner classifier that reads the owner name and the use code. A parcel counts as a trust parcel when the classifier calls the owner a trust, which happens when the name contains TRUST or a trustee word (TR, TRS, TRE, TTEE, TRUSTEE and similar) and no earlier rule has claimed it. Government owners and names containing LLC are sorted before trusts, and a trust company or bank-and-trust name is never counted as a trust. Names that also carry a bank, company or public body marker (BANK, NATIONAL ASSOCIATION, BOARD OF TRUSTEES, CONSERVATION, HOUSING, INC, LLC, MORTGAGE, CERTIFICATEHOLDERS and similar) are set aside and counted in `excluded_institutional_trustee_parcels`. That removes mortgage securitization trusts, boards of trustees, conservation land trusts and similar owners that are not a family holding its own home.

Each remaining trust parcel is then read for three things.

1. **Kind.** REV, REVOCABLE, RLT or LIVING TRUST means revocable (a living trust is revocable by default). IRREV or IRREVOCABLE means irrevocable. TESTAMENTARY means a trust created by a will. A land trust is a named land trust, a numbered trust ("TRUST NO 12") or a trust with a title company or land trust service company as trustee. Anything else is unstated.
2. **Trustees.** TRS, TTEES or TRUSTEES, or two names joined by "&" with a trustee word, means joint trustees. A single trustee word with one name means a single trustee. A name with no trustee word at all ("SMITH FAMILY TRUST") means the trust itself is written as owner.
3. **Homestead.** A parcel counts as a homestead when the roll shows a homestead exemption value for it (`JV_HMSTD` greater than zero).

Family trust counts are the trust counts minus land trusts.

## Limits

- **The classification reads the owner name only, never the trust document.** Nothing here confirms that a trust exists, what its terms are or who the beneficiaries are.
- **The owner name field is short and often truncated.** A word such as REVOCABLE is frequently cut off or never written, so about 78% of trust parcels do not state whether the trust is revocable or irrevocable. Most of the unstated trusts are probably revocable living trusts, but the data does not show that, and the revocable count is a floor.
- **Six counties undercount trusts.** In Alachua (0.14% of residential parcels in a family trust), Manatee (0.25%), Baker (0.73%), Clay (0.77%), Gadsden (0.84%) and Citrus (0.92%), the property roll records the owner's own name with no trustee designation, so the name test cannot see the trust. Manatee shows 552 homes in a family trust against 38,308 in neighboring Sarasota. The roll's fiduciary name and code fields (`FIDU_NAME`, `FIDU_CD`) are empty statewide and cannot fill the gap. These six counties are marked `unreliable` in `trust_designation_on_roll` (the rule is a family trust share under 1.0%) and should not be ranked. The statewide totals include them as they stand, so the true statewide figure is somewhat higher.
- **Homestead counts vary with county recording practice too.** In Broward only 754 of 21,702 homes in a family trust (3%) show a homestead exemption, and in Palm Beach 2,618 of 30,446 (9%), against 44% to 71% in every other county with more than 10,000 homes in a family trust. Read the homestead counts for those two counties as a floor; the column `homestead_on_roll` marks them `floor`.
- **Banks, companies and public bodies named as trustee are excluded** and counted separately (4,911 parcels statewide). A few family trusts whose names happen to contain one of the institution words are excluded with them.
- **Land trusts are parsed out** (numbered, named, and those with a corporate trustee) and reported separately from family trusts. A land trust written without any of those markers is counted as a family trust.
- **"Homestead" means the parcel shows a homestead exemption value on the roll.** It does not mean a court has found the property to be protected homestead for inheritance or creditor purposes.
- **"Residential" follows the Department of Revenue use codes** and includes vacant residential lots, so a residential parcel is not always a house.
- **The roll is the 2026 preliminary roll, except Citrus, which is final.** Preliminary values and exemptions can change before the roll is certified.
- **Just value** is the property appraiser's market value on the roll, not a sale price.

## Not legal advice

This is reference data, not legal advice, and using it creates no attorney-client relationship. Whether a trust suits a particular home depends on facts this table cannot hold. The guides on [the Florida revocable living trust](https://stepuplaw.com/florida-revocable-living-trust/) and [putting a Florida homestead in a revocable trust](https://stepuplaw.com/florida-homestead-in-a-revocable-trust/) explain the rules.

## License

The data is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may use it commercially, modify it and build products on it with credit.

## Citation

Klagge, Kevin D. *Florida Homes Held in Trust, by County (2026)*. StepUpLaw, 2026. https://stepuplaw.com/data/florida-homes-held-in-trust/

`CITATION.cff` holds the same citation in machine-readable form. Corrections are welcome at office@stepuplaw.com.
