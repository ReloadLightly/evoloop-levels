import unittest
from evoloop.developmental import partition,retention_bounds,panel_bounds,strict_interval_superiority,conjunction
from scripts.developmental_measure import search_key
class DevelopmentalMeasureTests(unittest.TestCase):
 def test_unresolved_retained(self):
  self.assertEqual(partition([{'transmission_confirmed':True},{'transmission_confirmed':False}]),{'Q':1,'R':1,'C':2})
 def test_false_dominates_missing(self):
  self.assertFalse(conjunction([None,False]));self.assertIsNone(conjunction([True,None]))
 def test_empty_measured_zero(self): self.assertEqual(partition([]),{'Q':0,'R':0,'C':0})
 def test_interval_and_zero(self):
  b=retention_bounds({'Q':2,'C':3},{'Q':4,'C':5});self.assertEqual(b['lower'],{'numerator':2,'denominator':5});self.assertEqual(b['upper'],{'numerator':3,'denominator':4})
  self.assertEqual(retention_bounds({'Q':1,'C':2},{'Q':0,'C':2})['status'],'unbounded_upper')
  self.assertEqual(retention_bounds({'Q':0,'C':0},{'Q':0,'C':0})['status'],'undefined_zero_detected_control')
 def test_panel_does_not_pool(self):
  b=panel_bounds([({'Q':1,'C':1},{'Q':2,'C':2}),({'Q':2,'C':2},{'Q':3,'C':3})]);self.assertEqual(b['lower'],{'numerator':7,'denominator':12})
 def test_tie_fails_and_unknown_kept(self):
  b=retention_bounds({'Q':1,'C':1},{'Q':1,'C':1});self.assertFalse(strict_interval_superiority(b,[b]))
  x=retention_bounds({'Q':0,'C':1},{'Q':0,'C':1});self.assertIsNone(strict_interval_superiority(b,[x]))
 def test_cache_endpoint_identity_and_config_bound(self):
  self.assertNotEqual(search_key('a',None,{}),search_key('a','known',{}))
  self.assertNotEqual(search_key('a',None,{}),search_key('a',None,{},True))
  self.assertNotEqual(search_key('a',None,{}),search_key('a',None,{'horizon':1}))
if __name__=='__main__':unittest.main()
