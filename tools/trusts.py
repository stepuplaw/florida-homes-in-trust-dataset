"""Florida real property held in trust, by county (2026 NAL roll). Built 2026-09-30 for StepUp Law.

Copied into the florida-homes-in-trust-dataset repository for transparency. It does not run on its own:
it imports classify.py (owner_type, is_residential) and build.py (COUNTIES, num) from the fl-owners
project, and reads the Department of Revenue NAL zip files from raw/. Only the aggregate outputs are
published; the owner-name samples it writes to private/ are never published.

Takes every parcel the owner classifier calls a trust (classify.owner_type == "trust") and reads the
owner name for what it says about the trust:

  kind      revocable    REV, REVOCABLE, RLT, LIVING TRUST, LIV TR (a living trust is revocable by default)
            irrevocable  IRREV, IRREVOCABLE, IRR TR
            land         LAND TRUST, or a numbered trust ("TRUST NO 12", "TR #4", "TRUST 1057")
            unstated     the name does not say (many owners are written "SMITH JOHN TR")
  trustees  joint        TRS, TTEES, TRUSTEES, CO-TR, or two names joined by & with a trustee word
            single       TR, TRE, TTEE, TRUSTEE with one name
            trust_named  the trust itself is the owner ("SMITH FAMILY TRUST"), no trustee word

and whether the parcel carries a homestead exemption (JV_HMSTD > 0), which in Florida a trust-held home
keeps when the grantor holds the beneficial interest.

Limits, stated wherever the numbers are used: the roll's owner field is short and often truncated, so
"REVOCABLE" can be cut off and the kind reads as unstated; the classification is from the NAME only,
never from the trust document; a parcel owned by a bank as trustee is not counted as a trust
(classify.py sends it to corporation). Aggregates only; no names leave private/.

Usage:  python3 tools/trusts.py [--workers 8]
Writes: data/trusts_by_county.csv, data/trusts_statewide.json, private/trust_name_samples.txt
"""
import argparse, collections, csv, glob, io, json, os, random, re, sys, zipfile
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from classify import owner_type, is_residential  # noqa: E402
from build import COUNTIES, num  # noqa: E402

IRREV = re.compile(r"\b(IRREV\w*|IRR TR|IRR TRUST|IRRV)\b")
REV = re.compile(r"\b(REV|REVOC\w*|RLT|LIVING TRUST|LIVING TR|LIV TR|LIV TRUST|LVG TR|LVG TRUST)\b")
LAND = re.compile(r"\b(LAND TRUST|LAND TR)\b|\bTRUST\s*(NO\.?|NUMBER|#)\s*\d|\bTR\s*(NO\.?|#)\s*\d|\bTRUST\s+\d{2,}")
TESTAMENTARY = re.compile(r"\bTESTAMENTARY\b|\bTEST TR\b")
# Institutions and public bodies the name pattern catches: banks (often truncated), boards of trustees,
# conservation and community land trusts, housing trusts, companies named as trustee. Not family trusts.
INSTITUTION = re.compile(r"\b(BANK|NATIONAL ASSOC\w*|NATL ASSOC\w*|NATIONAL ASS\w*|BOARD OF TRUSTEES|TRUSTEES OF|CONSERVATION|COMMUNITY LAND|CONSERVANCY|HOUSING|CHURCH|MINISTR\w*|INC|LLC|L L C|CORP\w*|COMPANY|REIT|AUTHORITY|DISTRICT|UNIVERSITY|COLLEGE|FOUNDATION|ASSOCIATION|ASSN|FEDERAL|MORTGAGE|SECURITIES|CERTIFICATEHOLDERS|CERTIFICATE HOLDERS|PASS THROUGH|SERIES \d)\b")
JOINT = re.compile(r"\b(TRS|TTEES|TRUSTEES|CO[- ]?TR\w*|CO[- ]?TRUSTEES?)\b")
TRUSTEE_WORD = re.compile(r"\b(TR|TRE|TTEE|TRUSTEE|TRSTEE)\b")


LAND_NAMED = re.compile(r"\b(LAND TRUST|LAND TR)\b")
LAND_NUMBERED = re.compile(r"\bTRUST\s*(NO\.?|NUMBER|#)\s*\d|\bTR\s*(NO\.?|#)\s*\d|\bTRUST\s+\d{2,}")
# A company acting as trustee of a Florida land trust (title companies, "land trust service" firms). These
# hold title for private beneficiaries under the land trust statute, so they are counted as land trusts
# with a corporate trustee rather than dropped with the banks and public bodies.
LAND_CORP = re.compile(r"\b(LAND TRUST SERV\w*|TITLE\b.*\b(TR|TRS|TRUSTEE|TTEE)\b|(TR|TRUSTEE|TTEE)\b.*\bTITLE)")


def land_kind(n):
    if LAND_CORP.search(n): return "land_corporate_trustee"
    if LAND_NUMBERED.search(n): return "land_numbered"
    if LAND_NAMED.search(n): return "land_named"
    return None


def kind(n):
    if TESTAMENTARY.search(n): return "testamentary"
    if IRREV.search(n): return "irrevocable"
    if REV.search(n): return "revocable"
    if LAND.search(n): return "land"
    return "unstated"


def trustees(n):
    if JOINT.search(n): return "joint"
    if TRUSTEE_WORD.search(n):
        return "joint" if ("&" in n or " + " in n) else "single"
    return "trust_named"


def process(path):
    z = zipfile.ZipFile(path)
    name = [x for x in z.namelist() if x.lower().endswith((".csv", ".txt"))][0]
    rd = csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1", newline=""))
    rd.fieldnames = [f.strip() for f in rd.fieldnames]
    c = collections.Counter()
    jv = collections.Counter()
    samples = collections.defaultdict(list)
    co = None
    for r in rd:
        co = co or num(r.get("CO_NO"))
        uc = (r.get("DOR_UC") or "").strip()
        res = is_residential(uc)
        c["parcels"] += 1
        if res: c["residential"] += 1
        n = " ".join((r.get("OWN_NAME") or "").upper().split())
        if owner_type(n, uc) != "trust":
            continue
        lk = land_kind(n)
        if INSTITUTION.search(n) and lk != "land_corporate_trustee":
            c["excluded_institution"] += 1
            if len(samples["_excluded"]) < 40 and random.random() < 0.01: samples["_excluded"].append(n)
            continue
        v = num(r.get("JV"))
        hx = num(r.get("JV_HMSTD")) > 0
        k, t = kind(n), trustees(n)
        if lk:
            k = "land"
            c[f"land_{lk}"] += 1
            if res: c[f"res_land_{lk}"] += 1
            if hx: c[f"hx_land_{lk}"] += 1
        c["trust"] += 1; jv["trust"] += v
        c[f"kind_{k}"] += 1; c[f"trustees_{t}"] += 1
        if res:
            c["trust_residential"] += 1; jv["trust_residential"] += v
            c[f"res_kind_{k}"] += 1
        if hx:
            c["trust_homestead"] += 1; c[f"hx_kind_{k}"] += 1
        if len(samples[k]) < 40 and random.random() < 0.02:
            samples[k].append(n)
    return co, dict(c), dict(jv), dict(samples)


KINDS = ["revocable", "irrevocable", "testamentary", "land", "unstated"]
TRUSTEES = ["single", "joint", "trust_named"]
LAND_KINDS = ["land_numbered", "land_named", "land_corporate_trustee"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    random.seed(7)
    files = sorted(glob.glob(os.path.join(ROOT, "raw", "*.zip")))
    with Pool(a.workers) as p:
        results = p.map(process, files)
    seen = collections.Counter(r[0] for r in results)
    assert len(seen) == 67 and all(v == 1 for v in seen.values()), seen
    rows, tot, tjv, samp = [], collections.Counter(), collections.Counter(), collections.defaultdict(list)
    for co, c, jv, s in sorted(results, key=lambda x: COUNTIES[x[0]]):
        tot.update(c); tjv.update(jv)
        for k, v in s.items(): samp[k].extend(v)
        t = c.get("trust", 0)
        row = {
            "county": COUNTIES[co], "parcels": c["parcels"], "trust_parcels": t,
            "pct_parcels_in_trust": round(100 * t / c["parcels"], 2) if c["parcels"] else 0,
            "trust_just_value": jv.get("trust", 0),
            "residential_parcels": c.get("residential", 0), "trust_residential_parcels": c.get("trust_residential", 0),
            "pct_residential_in_trust": round(100 * c.get("trust_residential", 0) / c["residential"], 2) if c.get("residential") else 0,
            "trust_homestead_parcels": c.get("trust_homestead", 0),
        }
        for k in KINDS: row[f"kind_{k}"] = c.get(f"kind_{k}", 0)
        for k in TRUSTEES: row[f"trustees_{k}"] = c.get(f"trustees_{k}", 0)
        for k in LAND_KINDS: row[k] = c.get(f"land_{k}", 0)
        row["family_trust_parcels"] = t - c.get("kind_land", 0)
        row["family_trust_residential_parcels"] = c.get("trust_residential", 0) - c.get("res_kind_land", 0)
        row["family_trust_homestead_parcels"] = c.get("trust_homestead", 0) - c.get("hx_kind_land", 0)
        row["pct_residential_in_family_trust"] = round(100 * row["family_trust_residential_parcels"] / c["residential"], 2) if c.get("residential") else 0
        # Some property appraisers write the owner's own name with no trustee designation (Manatee, for one,
        # writes a bare personal name), and FIDU_NAME/FIDU_CD are empty statewide, so the name test cannot see
        # the trust. A county under 1% of homes in a family trust is flagged rather than ranked.
        row["trust_designation_on_roll"] = "unreliable" if row["pct_residential_in_family_trust"] < 1.0 else "recorded"
        rows.append(row)
    with open(os.path.join(ROOT, "data", "trusts_by_county.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    t = tot["trust"]
    summary = {
        "source": "Florida Department of Revenue 2026 NAL real property roll (66 counties preliminary, Citrus final)",
        "built": "2026-09-30",
        "parcels": tot["parcels"], "trust_parcels": t, "pct_parcels_in_trust": round(100 * t / tot["parcels"], 2),
        "trust_just_value": tjv["trust"],
        "residential_parcels": tot["residential"], "trust_residential_parcels": tot["trust_residential"],
        "pct_residential_in_trust": round(100 * tot["trust_residential"] / tot["residential"], 2),
        "trust_residential_just_value": tjv["trust_residential"],
        "trust_homestead_parcels": tot["trust_homestead"],
        "excluded_institutional_trustee_parcels": tot["excluded_institution"],
        "kind": {k: tot[f"kind_{k}"] for k in KINDS},
        "kind_residential": {k: tot[f"res_kind_{k}"] for k in KINDS},
        "kind_homestead": {k: tot[f"hx_kind_{k}"] for k in KINDS},
        "trustees": {k: tot[f"trustees_{k}"] for k in TRUSTEES},
        "land": {k: tot[f"land_{k}"] for k in LAND_KINDS},
        "land_residential": {k: tot[f"res_land_{k}"] for k in LAND_KINDS},
        "land_homestead": {k: tot[f"hx_land_{k}"] for k in LAND_KINDS},
        "family_trust_parcels": t - tot["kind_land"],
        "family_trust_residential_parcels": tot["trust_residential"] - tot["res_kind_land"],
        "family_trust_homestead_parcels": tot["trust_homestead"] - tot["hx_kind_land"],
        "limits": "Classified from the owner NAME on the roll, which is short and often truncated; a trust whose name does not say revocable or irrevocable is counted as unstated. Banks, companies and public bodies named as trustee (mortgage-securitization trusts, boards of trustees, conservation and housing trusts) are excluded and counted separately.",
    }
    with open(os.path.join(ROOT, "data", "trusts_statewide.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(ROOT, "private", "trust_name_samples.txt"), "w") as f:
        for k, v in samp.items():
            f.write(f"== {k}\n" + "\n".join(v[:60]) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
