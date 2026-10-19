import unittest
from axis_assignment import axis_fill_interval
class AxisFillTests(unittest.TestCase):
 def test_fill_tracks_output_without_binary_activation(self):
  self.assertEqual(axis_fill_interval(.05,False),(0,.05))
  self.assertEqual(axis_fill_interval(1,False),(0,1))
  self.assertEqual(axis_fill_interval(0,True),(.5,.5))
  self.assertEqual(axis_fill_interval(.2,True),(.5,.6))
  self.assertEqual(axis_fill_interval(-1,True),(0,.5))
  self.assertEqual(axis_fill_interval(1,True),(.5,1))
  self.assertEqual(axis_fill_interval(float('nan'),True),(.5,.5))
