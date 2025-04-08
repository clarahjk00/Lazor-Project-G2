import unittest
from Main_Code_Block import Point, Laser, ReflectBlock, OpaqueBlock, RefractBlock, Board

class TestGame(unittest.TestCase):
    def point_test(self):
        p1 = Point(1, 1)
        p2 = Point(2, 2)
        result = p1 + p2
        expected = Point(3, 3)
        self.assertEqual(result, expected)


    def reflection_test(self):
        block = ReflectBlock(Point(2, 2))
        laser = Laser(Point(2, 2), Point(1, -1))
        reflected_laser = block.interact(laser)
        self.assertEqual(reflected_laser[0].direction, Point(-1, 1))


    def opaque_test(self):
        block = OpaqueBlock(Point(1, 1))
        opqaue_laser = block.interact(Laser(Point(1, 1), Point(1, 0)))
        self.assertEqual(opqaue_laser, [])


    def refraction_test(self):
        block = RefractBlock(Point(3, 3))
        laser = Laser(Point(3, 3), Point(1, -1))
        refracted_laser = block.interact(laser)
        self.assertEqual(len(refracted_laser), 2)
        self.assertIn(Laser(Point(3, 3), Point(1, 1)), refracted_laser)
        self.assertIn(Laser(Point(3, 3), Point(-1, -1)), refracted_laser)


if __name__ == "__main__":
    unittest.main()