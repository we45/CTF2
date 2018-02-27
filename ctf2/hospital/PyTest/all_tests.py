from session_fixation_attack import session_fixation
from sql_injection_attack import sql_injection
from ajax_idor_attack import ajax_idor
from csrf_attack import csrf
from xss_attack import xss
from fixtures import webdriver
import pytest
from results import display_results,delete_index
from zap_test import scan_zap
import time

@pytest.mark.incremental
class TestSecDevOps:
	done = False
	complete = False
	# @pytest.mark.order1
	def test_1(self):
		delete_index()

	# @pytest.mark.order2
	def test_2(self,webdriver):
		csrf(webdriver)

	# @pytest.mark.order3
	def test_3(self,webdriver):
		session_fixation(webdriver,email = 'steve.jobs@we45.com')

	# @pytest.mark.order4
	def test_4(self,webdriver):
		ajax_idor(webdriver)

	# @pytest.mark.order5
	def test_5(self,webdriver):
		xss(webdriver)	

	# @pytest.mark.order6
	def test_6(self,webdriver):
		sql_injection()
		TestSecDevOps.done = True

	def test_7(self):
		if TestSecDevOps.done:
			scan_zap()
			TestSecDevOps.complete = True


	# @pytest.mark.order8
	def test_8(self):
		time.sleep(10)
		if TestSecDevOps.complete:
			display_results()	

	


