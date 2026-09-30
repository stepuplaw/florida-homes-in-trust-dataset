# Findings

Headline numbers from the 2026 Florida Department of Revenue NAL property roll (66 counties preliminary, Citrus final), built on September 30, 2026. Every count is a parcel count. The statewide totals include six counties whose rolls undercount trusts (Section 4), so the true statewide figures are somewhat higher.

## 1. Statewide

| Measure | All property | Residential |
|---|---|---|
| Parcels on the roll | 11,090,196 | 9,830,053 |
| Held in trust (family and land trusts) | 651,646 (5.88%) | 600,542 (6.11%) |
| Just value of the trust parcels | $374.5 billion | $347.5 billion |
| In a family trust | 630,766 | 582,392 (5.92%) |
| In a land trust | 20,880 | 18,150 |

- **Homesteads in trust.** 270,615 trust parcels show a homestead exemption on the roll, and 268,631 of them are in a family trust. That is 46% of the homes held in a family trust.
- **Across the 61 counties whose rolls record the trustee designation**, 579,453 of 9,251,791 residential parcels (6.26%) are in a family trust.
- **Excluded.** 4,911 parcels name a bank, company or public body as trustee and are not counted as trusts.

## 2. What the owner name says

| Kind | All trust parcels | Residential | Homestead |
|---|---|---|---|
| Revocable or living trust | 118,647 (18.2%) | 111,258 | 51,199 |
| Irrevocable | 3,598 | 3,339 | 594 |
| Testamentary | 115 | 58 | 9 |
| Land trust | 20,880 | 18,150 | 1,984 |
| Not stated | 508,406 (78.0%) | 467,737 | 216,829 |

| Trustees | Parcels |
|---|---|
| One trustee named | 273,507 |
| Two or more trustees named | 98,136 |
| Trust written as owner, no trustee word | 280,003 |

| Land trust type | All | Residential | Homestead |
|---|---|---|---|
| Numbered ("TRUST NO 12") | 6,759 | 5,984 | 986 |
| Named ("LAND TRUST") | 13,585 | 11,711 | 962 |
| Title or land trust company as trustee | 536 | 455 | 36 |

## 3. Counties

Highest share of residential parcels in a family trust (counties marked `recorded` only):

| County | Share | Homes in a family trust | Of which homestead |
|---|---|---|---|
| Collier | 19.15% | 45,852 | 21,485 |
| Sarasota | 13.16% | 38,308 | 21,123 |
| Lee | 12.15% | 64,041 | 29,159 |
| Indian River | 12.09% | 10,572 | 6,154 |
| Sumter | 11.45% | 10,927 | 7,757 |
| Charlotte | 9.31% | 19,508 | 8,571 |
| Pinellas | 8.60% | 34,740 | 18,627 |
| Hernando | 8.20% | 8,837 | 4,905 |
| Volusia | 7.91% | 21,657 | 10,140 |
| Okaloosa | 7.66% | 7,731 | 3,037 |

Most homes in a family trust: Lee (64,041), Miami-Dade (51,589), Collier (45,852), Sarasota (38,308), Pinellas (34,740), Palm Beach (30,446) and Hillsborough (29,012).

Most land trusts: Duval (2,139), Monroe (1,745), Orange (1,629), Broward (1,530), Polk (1,525) and Pasco (1,406).

## 4. Counties that undercount

Six county rolls record the owner's own name with no trustee designation, so the name test cannot see the trust. The roll's `FIDU_NAME` and `FIDU_CD` fields are empty statewide and cannot fill the gap. These counties are marked `unreliable` in `trust_designation_on_roll` and should not be ranked.

| County | Share of residential parcels in a family trust |
|---|---|
| Alachua | 0.14% |
| Manatee | 0.25% |
| Baker | 0.73% |
| Clay | 0.77% |
| Gadsden | 0.84% |
| Citrus | 0.92% |

Manatee shows 552 homes in a family trust against 38,308 in neighboring Sarasota.

The homestead counts in Broward (754 of 21,702 homes in a family trust, 3%) and Palm Beach (2,618 of 30,446, 9%) are far below the 44% to 71% seen in every other county with more than 10,000 homes in a family trust, which points to a recording difference rather than a real one. Read those two homestead counts as a floor; the column `homestead_on_roll` marks them `floor`.
