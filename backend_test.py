#!/usr/bin/env python3
"""
CloudReady ERP Scorecard Backend API Tests
Tests all backend endpoints for the ERP Cloud Readiness assessment platform.
"""

import requests
import json
import sys
from datetime import datetime

# Base URL from environment
BASE_URL = "https://scorecloud.preview.emergentagent.com/api"

class ERPScorecardTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.assessment_id = None
        self.profile_id = None
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        if data and not success:
            print(f"   Response: {json.dumps(data, indent=2)}")
        print()
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'CloudReady ERP Scorecard API':
                    self.log_test("API Root", True, f"Version: {data.get('version', 'N/A')}")
                    return True
                else:
                    self.log_test("API Root", False, "Unexpected response format", data)
                    return False
            else:
                self.log_test("API Root", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("API Root", False, f"Exception: {str(e)}")
            return False
    
    def test_questions_api(self):
        """Test Questions API - Should return at least 25 active questions"""
        try:
            response = self.session.get(f"{self.base_url}/questions")
            if response.status_code == 200:
                data = response.json()
                questions = data.get('questions', [])
                
                if len(questions) >= 25:
                    # Verify question structure
                    sample_q = questions[0]
                    required_fields = ['id', 'qid', 'pillar', 'gate', 'text', 'effort', 'fixHint', 'riskText']
                    missing_fields = [field for field in required_fields if field not in sample_q]
                    
                    if not missing_fields:
                        # Verify pillars P1-P10 and gates G1-G5
                        pillars = set(q['pillar'] for q in questions)
                        gates = set(q['gate'] for q in questions)
                        expected_pillars = {f'P{i}' for i in range(1, 11)}
                        expected_gates = {f'G{i}' for i in range(1, 6)}
                        
                        if expected_pillars.issubset(pillars) and gates.issubset(expected_gates):
                            self.log_test("Questions API", True, f"Found {len(questions)} questions with all pillars P1-P10 and gates")
                            return True
                        else:
                            self.log_test("Questions API", False, f"Missing pillars or gates. Found pillars: {sorted(pillars)}, gates: {sorted(gates)}")
                            return False
                    else:
                        self.log_test("Questions API", False, f"Missing required fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Questions API", False, f"Expected at least 25 questions, got {len(questions)}")
                    return False
            else:
                self.log_test("Questions API", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Questions API", False, f"Exception: {str(e)}")
            return False
    
    def test_settings_api(self):
        """Test Settings API - Should return default settings"""
        try:
            response = self.session.get(f"{self.base_url}/settings")
            if response.status_code == 200:
                data = response.json()
                settings = data.get('settings', {})
                
                if 'weights' in settings and 'pricing' in settings:
                    weights = settings['weights']
                    # Verify weights total 100%
                    total_weight = sum(weights.values())
                    
                    if total_weight == 100:
                        # Verify pricing for both currencies
                        pricing = settings['pricing']
                        if 'tierA' in pricing and 'tierB' in pricing:
                            tier_a = pricing['tierA']
                            tier_b = pricing['tierB']
                            if 'INR' in tier_a and 'AED' in tier_a and 'INR' in tier_b and 'AED' in tier_b:
                                self.log_test("Settings API", True, f"Weights total: {total_weight}%, Pricing configured for INR/AED")
                                return True
                            else:
                                self.log_test("Settings API", False, "Missing currency pricing")
                                return False
                        else:
                            self.log_test("Settings API", False, "Missing pricing tiers")
                            return False
                    else:
                        self.log_test("Settings API", False, f"Weights total {total_weight}%, expected 100%")
                        return False
                else:
                    self.log_test("Settings API", False, "Missing weights or pricing", settings)
                    return False
            else:
                self.log_test("Settings API", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Settings API", False, f"Exception: {str(e)}")
            return False
    
    def test_start_assessment(self):
        """Test Assessment Flow - POST /api/start-assessment"""
        try:
            profile_data = {
                "name": "John Manufacturing",
                "email": "john@manufacturing.com",
                "companyName": "Manufacturing Corp Ltd",
                "role": "IT Director",
                "erp": "Epicor",
                "epicorVersion": "10.2.700",
                "timeline": "6-12 months"
            }
            
            response = self.session.post(f"{self.base_url}/start-assessment", json=profile_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'assessmentId' in data and 'profileId' in data:
                    self.assessment_id = data['assessmentId']
                    self.profile_id = data['profileId']
                    self.log_test("Start Assessment", True, f"Created assessment: {self.assessment_id}")
                    return True
                else:
                    self.log_test("Start Assessment", False, "Missing success flag or IDs", data)
                    return False
            else:
                self.log_test("Start Assessment", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Start Assessment", False, f"Exception: {str(e)}")
            return False
    
    def test_save_answers(self):
        """Test Answers API - POST /api/save-answers"""
        if not self.assessment_id:
            self.log_test("Save Answers", False, "No assessment ID available")
            return False
            
        try:
            # Create 25 sample answers with scores 2-3 (realistic scores)
            sample_answers = []
            for i in range(1, 26):
                sample_answers.append({
                    "questionId": f"q{i}",  # This will be replaced with actual question IDs
                    "score": 2 if i % 3 == 0 else 3  # Mix of scores 2 and 3
                })
            
            # First get actual question IDs
            questions_response = self.session.get(f"{self.base_url}/questions")
            if questions_response.status_code == 200:
                questions_data = questions_response.json()
                questions = questions_data.get('questions', [])
                
                # Update answers with real question IDs
                for i, answer in enumerate(sample_answers):
                    if i < len(questions):
                        answer['questionId'] = questions[i]['id']
            
            answers_data = {
                "assessmentId": self.assessment_id,
                "answers": sample_answers
            }
            
            response = self.session.post(f"{self.base_url}/save-answers", json=answers_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Save Answers", True, f"Saved {len(sample_answers)} answers")
                    return True
                else:
                    self.log_test("Save Answers", False, "Success flag not set", data)
                    return False
            else:
                self.log_test("Save Answers", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Save Answers", False, f"Exception: {str(e)}")
            return False
    
    def test_calculate_results(self):
        """Test Results Calculation - POST /api/calculate-results"""
        if not self.assessment_id:
            self.log_test("Calculate Results", False, "No assessment ID available")
            return False
            
        try:
            calc_data = {"assessmentId": self.assessment_id}
            
            response = self.session.post(f"{self.base_url}/calculate-results", json=calc_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'results' in data:
                    results = data['results']
                    
                    # Verify scoring engine results
                    required_fields = ['overallScore', 'pillarResults', 'gateResults', 'topRisks', 'quickWins', 'decision', 'roadmap']
                    missing_fields = [field for field in required_fields if field not in results]
                    
                    if not missing_fields:
                        overall_score = results['overallScore']
                        pillar_results = results['pillarResults']
                        gate_results = results['gateResults']
                        decision = results['decision']
                        
                        # Verify overall score is 0-100
                        if 0 <= overall_score <= 100:
                            # Verify pillar results have RAG status
                            pillar_rags = [p.get('rag') for p in pillar_results.values()]
                            valid_rags = all(rag in ['Green', 'Amber', 'Red'] for rag in pillar_rags)
                            
                            # Verify gate results have PASS/CONDITIONAL/FAIL
                            gate_statuses = [g.get('status') for g in gate_results.values()]
                            valid_statuses = all(status in ['PASS', 'CONDITIONAL', 'FAIL'] for status in gate_statuses)
                            
                            # Verify decision is valid
                            valid_decision = decision in ['GO', 'GO with conditions', 'NO-GO']
                            
                            if valid_rags and valid_statuses and valid_decision:
                                self.log_test("Calculate Results", True, 
                                            f"Overall: {overall_score}%, Decision: {decision}, "
                                            f"Pillars: {len(pillar_results)}, Gates: {len(gate_results)}")
                                return True
                            else:
                                self.log_test("Calculate Results", False, "Invalid RAG/status/decision values")
                                return False
                        else:
                            self.log_test("Calculate Results", False, f"Overall score {overall_score} not in 0-100 range")
                            return False
                    else:
                        self.log_test("Calculate Results", False, f"Missing result fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Calculate Results", False, "Missing success flag or results", data)
                    return False
            else:
                self.log_test("Calculate Results", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Calculate Results", False, f"Exception: {str(e)}")
            return False
    
    def test_get_results(self):
        """Test Results Retrieval - GET /api/results/:assessmentId"""
        if not self.assessment_id:
            self.log_test("Get Results", False, "No assessment ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/results/{self.assessment_id}")
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    result = data['result']
                    if 'overallScore' in result and 'pillarResults' in result:
                        self.log_test("Get Results", True, f"Retrieved results for assessment {self.assessment_id}")
                        return True
                    else:
                        self.log_test("Get Results", False, "Missing result data", result)
                        return False
                else:
                    self.log_test("Get Results", False, "Missing result field", data)
                    return False
            else:
                self.log_test("Get Results", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Results", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_questions(self):
        """Test Admin Questions API - POST /api/admin/questions"""
        try:
            # Test creating a new question
            new_question = {
                "qid": "TEST1",
                "pillar": "P1",
                "gate": "G1",
                "text": "Test question for admin API?",
                "whyItMatters": "Testing admin functionality",
                "evidenceToCheck": "Test evidence",
                "effort": "L",
                "fixHint": "Test fix hint",
                "riskText": "Test risk text",
                "active": True,
                "sortOrder": 999
            }
            
            response = self.session.post(f"{self.base_url}/admin/questions", json=new_question)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'question' in data:
                    created_question = data['question']
                    if 'id' in created_question:
                        self.log_test("Admin Questions", True, f"Created test question with ID: {created_question['id']}")
                        return True
                    else:
                        self.log_test("Admin Questions", False, "Missing question ID", created_question)
                        return False
                else:
                    self.log_test("Admin Questions", False, "Missing success flag or question", data)
                    return False
            else:
                self.log_test("Admin Questions", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Questions", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_settings(self):
        """Test Admin Settings API - POST /api/admin/settings"""
        try:
            # Test updating settings
            updated_settings = {
                "weights": {
                    "P1": 12, "P2": 12, "P3": 12, "P4": 12, "P5": 10,
                    "P6": 10, "P7": 10, "P8": 8, "P9": 7, "P10": 7
                },
                "currency": "INR",
                "pricing": {
                    "tierA": {"INR": 15999, "AED": 599},
                    "tierB": {"INR": 159999, "AED": 5999}
                },
                "guidedReviewLink": "https://calendly.com/test/guided-review"
            }
            
            # Add admin password header
            headers = {'x-admin-password': 'Murugan@369'}
            response = self.session.post(f"{self.base_url}/admin/settings", json=updated_settings, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Admin Settings", True, "Updated settings successfully")
                    return True
                else:
                    self.log_test("Admin Settings", False, "Success flag not set", data)
                    return False
            else:
                self.log_test("Admin Settings", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Settings", False, f"Exception: {str(e)}")
            return False

    def test_admin_verify(self):
        """Test Admin Password Verification - GET /api/admin/verify"""
        try:
            # Test with correct password
            headers = {'x-admin-password': 'Murugan@369'}
            response = self.session.get(f"{self.base_url}/admin/verify", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('valid') == True:
                    # Test with wrong password
                    wrong_headers = {'x-admin-password': 'wrongpassword'}
                    wrong_response = self.session.get(f"{self.base_url}/admin/verify", headers=wrong_headers)
                    if wrong_response.status_code == 200:
                        wrong_data = wrong_response.json()
                        if wrong_data.get('valid') == False:
                            self.log_test("Admin Verify", True, "Password verification working correctly")
                            return True
                        else:
                            self.log_test("Admin Verify", False, "Wrong password should return valid: false", wrong_data)
                            return False
                    else:
                        self.log_test("Admin Verify", False, f"Wrong password test failed: HTTP {wrong_response.status_code}")
                        return False
                else:
                    self.log_test("Admin Verify", False, "Correct password should return valid: true", data)
                    return False
            else:
                self.log_test("Admin Verify", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Verify", False, f"Exception: {str(e)}")
            return False

    def test_admin_stats(self):
        """Test Admin Dashboard Stats - GET /api/admin/stats"""
        try:
            headers = {'x-admin-password': 'Murugan@369'}
            response = self.session.get(f"{self.base_url}/admin/stats", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'stats' in data:
                    stats = data['stats']
                    required_fields = ['totalAssessments', 'completedAssessments', 'avgScore', 'completionRate', 'decisions']
                    missing_fields = [field for field in required_fields if field not in stats]
                    
                    if not missing_fields:
                        # Verify decisions structure
                        decisions = stats['decisions']
                        if 'GO' in decisions and 'GO with conditions' in decisions and 'NO-GO' in decisions:
                            self.log_test("Admin Stats", True, 
                                        f"Total: {stats['totalAssessments']}, Completed: {stats['completedAssessments']}, "
                                        f"Avg Score: {stats['avgScore']}%, Completion Rate: {stats['completionRate']}%")
                            return True
                        else:
                            self.log_test("Admin Stats", False, "Missing decision categories", decisions)
                            return False
                    else:
                        self.log_test("Admin Stats", False, f"Missing stats fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Admin Stats", False, "Missing stats field", data)
                    return False
            else:
                self.log_test("Admin Stats", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Stats", False, f"Exception: {str(e)}")
            return False

    def test_admin_assessments(self):
        """Test Admin Assessments List - GET /api/admin/assessments"""
        try:
            headers = {'x-admin-password': 'Murugan@369'}
            response = self.session.get(f"{self.base_url}/admin/assessments", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'assessments' in data:
                    assessments = data['assessments']
                    if len(assessments) > 0:
                        # Verify assessment structure
                        sample_assessment = assessments[0]
                        required_fields = ['id', 'name', 'email', 'companyName', 'completedAt', 'overallScore', 'decision']
                        missing_fields = [field for field in required_fields if field not in sample_assessment]
                        
                        if not missing_fields:
                            self.log_test("Admin Assessments", True, f"Retrieved {len(assessments)} completed assessments")
                            return True
                        else:
                            self.log_test("Admin Assessments", False, f"Missing assessment fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Admin Assessments", True, "No completed assessments found (expected for new system)")
                        return True
                else:
                    self.log_test("Admin Assessments", False, "Missing assessments field", data)
                    return False
            else:
                self.log_test("Admin Assessments", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Assessments", False, f"Exception: {str(e)}")
            return False

    def test_admin_about(self):
        """Test Admin About Us - GET and POST /api/admin/about"""
        try:
            # Test GET (public endpoint)
            response = self.session.get(f"{self.base_url}/admin/about")
            if response.status_code == 200:
                data = response.json()
                if 'aboutUs' in data:
                    about_us = data['aboutUs']
                    expected_fields = ['companyName', 'description', 'logoUrl', 'businessHours']
                    has_fields = all(field in about_us for field in expected_fields)
                    
                    if has_fields:
                        # Test POST (requires auth)
                        test_about = {
                            "companyName": "Test Company",
                            "description": "Test description for admin API testing",
                            "logoUrl": "https://example.com/logo.png",
                            "businessHours": "Mon-Fri 9AM-6PM"
                        }
                        
                        headers = {'x-admin-password': 'Murugan@369'}
                        post_response = self.session.post(f"{self.base_url}/admin/about", json=test_about, headers=headers)
                        if post_response.status_code == 200:
                            post_data = post_response.json()
                            if post_data.get('success'):
                                self.log_test("Admin About", True, "GET and POST About Us working correctly")
                                return True
                            else:
                                self.log_test("Admin About", False, "POST success flag not set", post_data)
                                return False
                        else:
                            self.log_test("Admin About", False, f"POST failed: HTTP {post_response.status_code}")
                            return False
                    else:
                        self.log_test("Admin About", False, "Missing aboutUs fields", about_us)
                        return False
                else:
                    self.log_test("Admin About", False, "Missing aboutUs field", data)
                    return False
            else:
                self.log_test("Admin About", False, f"GET failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin About", False, f"Exception: {str(e)}")
            return False

    def test_admin_contact(self):
        """Test Admin Contact Us - GET and POST /api/admin/contact"""
        try:
            # Test GET (public endpoint)
            response = self.session.get(f"{self.base_url}/admin/contact")
            if response.status_code == 200:
                data = response.json()
                if 'contactUs' in data:
                    contact_us = data['contactUs']
                    expected_fields = ['email', 'phone', 'address', 'linkedIn', 'twitter']
                    has_fields = all(field in contact_us for field in expected_fields)
                    
                    if has_fields:
                        # Test POST (requires auth)
                        test_contact = {
                            "email": "test@example.com",
                            "phone": "+91 1234567890",
                            "address": "123 Test Street, Test City",
                            "linkedIn": "https://linkedin.com/company/test",
                            "twitter": "https://twitter.com/test"
                        }
                        
                        headers = {'x-admin-password': 'Murugan@369'}
                        post_response = self.session.post(f"{self.base_url}/admin/contact", json=test_contact, headers=headers)
                        if post_response.status_code == 200:
                            post_data = post_response.json()
                            if post_data.get('success'):
                                self.log_test("Admin Contact", True, "GET and POST Contact Us working correctly")
                                return True
                            else:
                                self.log_test("Admin Contact", False, "POST success flag not set", post_data)
                                return False
                        else:
                            self.log_test("Admin Contact", False, f"POST failed: HTTP {post_response.status_code}")
                            return False
                    else:
                        self.log_test("Admin Contact", False, "Missing contactUs fields", contact_us)
                        return False
                else:
                    self.log_test("Admin Contact", False, "Missing contactUs field", data)
                    return False
            else:
                self.log_test("Admin Contact", False, f"GET failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Contact", False, f"Exception: {str(e)}")
            return False

    def test_admin_pricing(self):
        """Test Admin Pricing - GET /api/admin/pricing"""
        try:
            response = self.session.get(f"{self.base_url}/admin/pricing")
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['pricing', 'currency', 'guidedReviewLink', 'tierCBookingLink']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    pricing = data['pricing']
                    currency = data['currency']
                    if pricing and currency:
                        self.log_test("Admin Pricing", True, f"Pricing configured for {currency} currency")
                        return True
                    else:
                        self.log_test("Admin Pricing", False, "Empty pricing or currency")
                        return False
                else:
                    self.log_test("Admin Pricing", False, f"Missing pricing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Admin Pricing", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Pricing", False, f"Exception: {str(e)}")
            return False

    def test_admin_remove_test_question(self):
        """Test Admin Remove Test Questions - POST /api/admin/remove-test-question"""
        try:
            headers = {'x-admin-password': 'Murugan@369'}
            response = self.session.post(f"{self.base_url}/admin/remove-test-question", json={}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'deletedCount' in data:
                    deleted_count = data['deletedCount']
                    self.log_test("Admin Remove Test Question", True, f"Removed {deleted_count} test questions")
                    return True
                else:
                    self.log_test("Admin Remove Test Question", False, "Missing success flag or deletedCount", data)
                    return False
            else:
                self.log_test("Admin Remove Test Question", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Admin Remove Test Question", False, f"Exception: {str(e)}")
            return False

    def test_admin_unauthorized(self):
        """Test Admin Endpoints Without Authorization"""
        try:
            # Test admin stats without password
            response = self.session.get(f"{self.base_url}/admin/stats")
            if response.status_code == 401:
                # Test admin assessments without password
                response2 = self.session.get(f"{self.base_url}/admin/assessments")
                if response2.status_code == 401:
                    self.log_test("Admin Unauthorized", True, "Protected endpoints correctly return 401 without auth")
                    return True
                else:
                    self.log_test("Admin Unauthorized", False, f"Assessments endpoint should return 401, got {response2.status_code}")
                    return False
            else:
                self.log_test("Admin Unauthorized", False, f"Stats endpoint should return 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Unauthorized", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 60)
        print("CloudReady ERP Scorecard Backend API Tests")
        print(f"Base URL: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        tests = [
            ("API Root", self.test_api_root),
            ("Questions API", self.test_questions_api),
            ("Settings API", self.test_settings_api),
            ("Start Assessment", self.test_start_assessment),
            ("Save Answers", self.test_save_answers),
            ("Calculate Results", self.test_calculate_results),
            ("Get Results", self.test_get_results),
            ("Admin Questions", self.test_admin_questions),
            ("Admin Settings", self.test_admin_settings),
            # New Admin Dashboard Tests
            ("Admin Verify", self.test_admin_verify),
            ("Admin Stats", self.test_admin_stats),
            ("Admin Assessments", self.test_admin_assessments),
            ("Admin About", self.test_admin_about),
            ("Admin Contact", self.test_admin_contact),
            ("Admin Pricing", self.test_admin_pricing),
            ("Admin Remove Test Question", self.test_admin_remove_test_question),
            ("Admin Unauthorized", self.test_admin_unauthorized)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test_name} - Unexpected error: {str(e)}")
                failed += 1
        
        print("=" * 60)
        print(f"Test Results: {passed} passed, {failed} failed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return failed == 0

if __name__ == "__main__":
    tester = ERPScorecardTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)