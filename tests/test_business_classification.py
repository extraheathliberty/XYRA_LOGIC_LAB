import unittest
from xyra_logic.business_classification import validate_business_classification

class BusinessClassificationTests(unittest.TestCase):
    def test_missing_evidence_fails(self):
        r = validate_business_classification({"record_id":"31","business_name":"ITC","activity":"Wire products","entity_scope":"facility"})
        self.assertEqual(r["status"], "FAIL")
        self.assertIn("missing_activity_evidence",r["findings"])
    def test_structural_pass_still_review(self):
        path={"sector":"Industrials","industry_group":"Capital Goods","industry":"Machinery","sub_industry":"Example","code":"TEST"}
        p={"record_id":"31","business_name":"ITC","activity":"Wire products","entity_scope":"facility",
           "evidence":[{"url":"https://example.org","supports_activity":True}],
           "gics":path,"taxonomy":[path],"taxonomy_version":"TEST"}
        r=validate_business_classification(p)
        self.assertEqual(r["status"],"REVIEW")
        self.assertFalse(r["semantic_classification_verified"])
        self.assertFalse(r["production_admission"])
    def test_conflicting_path_fails(self):
        path={"sector":"Industrials","industry_group":"Capital Goods","industry":"Machinery","sub_industry":"Example","code":"TEST"}
        p={"record_id":"31","business_name":"ITC","activity":"Wire products","entity_scope":"facility",
           "evidence":[{"url":"https://example.org","supports_activity":True}],
           "gics":path,"taxonomy":[dict(path,code="OTHER")],"taxonomy_version":"TEST"}
        self.assertIn("invalid_gics_hierarchy",validate_business_classification(p)["findings"])
if __name__=="__main__":
    unittest.main()
