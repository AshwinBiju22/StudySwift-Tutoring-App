from django.test import TestCase
from studyswift.views import filter_inappropriate_content


class FilterContentTestCase(TestCase):
    def test_filter_inappropriate_content(self):
        # Acceptable
        inappropriate_content = "This is inappropriate content with the word shit."
        self.assertTrue(filter_inappropriate_content(inappropriate_content))

        # Acceptable
        appropriate_content = "This is appropriate content without any offensive words."
        self.assertFalse(filter_inappropriate_content(appropriate_content))

        # Erroneous
        appropriate_content = ""
        self.assertFalse(filter_inappropriate_content(appropriate_content))

        # Boundary
        appropriate_content = "This is inappropriate content that is disguisedshit ."
        self.assertTrue(filter_inappropriate_content(appropriate_content))
