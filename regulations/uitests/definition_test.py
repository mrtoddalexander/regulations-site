# vim: set encoding=utf-8
import unittest

from selenium.webdriver.support.ui import WebDriverWait

from regulations.uitests.base_test import BaseTest


class DefinitionTest(BaseTest, unittest.TestCase):
    job_name = 'Definitions test'

    def setUp(self):
        super(DefinitionTest, self).setUp()
        self.driver.set_window_size(1024, 600)
        self.driver.get(self.test_url + '/1005')
        html = self.driver.find_element_by_tag_name('html')
        WebDriverWait(self.driver, 30).until(
            lambda driver: 'selenium-start' in html.get_attribute('class'))

    def toc_nav(self, label_id):
        self.driver.find_element_by_id('panel-link').click()    # open ToC
        self.driver.find_element_by_id('nav-{}'.format(label_id)).click()
        self.driver.find_element_by_id('panel-link').click()    # close ToC

    def test_definition(self):
        self.toc_nav('1005-1')

        p = self.driver.find_element_by_id('1005-1-a')
        definition_link = p.find_element_by_link_text('Consumer')
        # term link should have correct data attr
        self.assertEqual(
            '1005-2-e', definition_link.get_attribute('data-definition'))

        definition_link.click()

        # term link should get active class
        self.assertIn('active', definition_link.get_attribute('class'))

        definition = self.driver.find_element_by_id('1005-2-e')
        definition_close_button = definition.find_element_by_css_selector(
            'h4 a')

        # definition should appear in sidebar
        self.assertGreater(len(definition.text), 20)
        definition_term = definition.find_element_by_xpath('.//dfn')
        self.assertEqual(u'“Consumer”', definition_term.text)

        definition_close_button.click()
        # definition should close
        self.assertFalse('active' in definition_link.get_attribute('class'))

        definition_link.click()

        # continue link should load full def
        definition.find_element_by_link_text(u'§ 1005.2(e)').click()
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.find_element_by_id('1005-2'))

    def test_definition_scope_notification(self):
        """Definitions can vary by subpart; when they do, we should receive a
        notification"""
        self.toc_nav('1005-11')

        p = self.driver.find_element_by_id('1005-11-b-2')
        new_definition_link = p.find_element_by_link_text('business days')
        self.driver.execute_script('window.scrollTo(0, 0);')
        new_definition_link.click()
        self.driver.find_element_by_id('1005-2-d')

        # navigate to a different subpart
        self.toc_nav('1005-30')

        # make sure that the scope notice displays
        warning = self.driver.find_element_by_class_name('definition-warning')
        self.assertTrue(warning.is_displayed())

    def test_definition_scope_load(self):
        """If a definition has a different scope, we _may_ be able to find the
        replacement"""
        self.toc_nav('1005-8')

        p = self.driver.find_element_by_id('1005-8-b')
        p.find_element_by_link_text('Error').click()

        # Navigate to a section with a different definition of error
        self.toc_nav('1005-33')

        definition_update_link = self.driver.find_element_by_class_name(
            'update-definition')
        definition_text = self.driver.find_element_by_class_name(
            'definition-text')

        # make sure text is grayed out
        self.assertIn('inactive', definition_text.get_attribute('class'))

        # load in scope definition
        definition_update_link.click()
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.find_element_by_id('1005-33-a-1'))
