from datetime import datetime, timedelta
import json
import requests
import string
import random
import hashlib
from pprint import pprint

upload_api = "http://localhost:8088/api/upload/"
first_name_file = "/opt/projects/lead_management/tradeshow/tradeshow/data/fnames.txt"
last_name_file = "/opt/projects/lead_management/tradeshow/tradeshow/data/lnames.txt"
email_domains = ["gmail.com", "yahoo.com", "msn.com", "hotmail.com"]
exhibitors = [(4, 'Times Godrej Properties', 'tgodreg'), (5, 'Times Unitech', 'tunitech'), (6, 'Times DLF', 'tdlf')]
question_answers = {}
question_answers[1] = ['Kharadi', 'Hadapsar', 'Viman Nagar', 'Kalyani nagar', 'Yerwada', 'Shivaji Nagar', 'Keshav Nagar', 'Wagholi', 'Hinjewadi', 'Baner', 'Pashan', 'City Area', 'Sinhgad Road']
question_answers[2] = ['Under Construction' , 'Ready to Move']
question_answers[3] = ['1st Floor', '2nd Floor', '3rd Floor' ,'3+ Floor', 'Above 5th Floor', 'Top Floor', '10th Floor']
question_answers[4] = ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']
question_answers[5] = ['Park', 'Gymnasium', 'Swimming Pool', 'Security Personnel', 'Power Backup', 'Gas Pipeline', 'Club house', 'Kids Play Area']
question_answers[6] = ['Investment', 'Living']
question_answers[7] = [ '0-20L', '20-40L', '40-60L', '60-80L', '80-100L', '1Cr+']
question_answers[8] = ['Bank Loan', 'Own Fund', 'Others']
question_answers[9] = ['0-10L', '10-20L', '20-30L', '30L+']
question_answers[10] = ['In weeks time', 'In months time', 'In couple of months']

qualifier_questions = {}
qualifier_questions['Times Godrej Properties'] = [(1, 31), (2, 32), (3, 33), (4, 34), (5, 35), (6, 36), (7, 37), (8, 38), (9, 39), (10, 40)]
qualifier_questions['Times Unitech'] = [(1, 41), (2, 42), (3, 43), (4, 44), (5, 45), (6, 46), (7, 47), (8, 48), (9, 49), (10, 50)]
qualifier_questions['Times DLF'] = [(1, 51), (2, 52), (3, 53), (4, 54), (5, 55), (6, 56), (7, 57), (8, 58), (9, 59), (10, 60)]


tradeshow_time_fromat = "%Y-%m-%d %H:%M:%S"
lead_types = ['hot', 'warm', 'cold']
scan_types = ['camera', 'manual']

exhibition_date = "2017-09-02"
tradeshowID = 2
batch_size = 100
lead_generation_count = 5000

def main():
	"""
	"""
	# Collect possible values of hours, minutes and seconds
	hours = [str(val).zfill(2) for val in range(10, 17)] # Consider time 10.00 AM till 5.00 PM
	minutes = [str(val).zfill(2) for val in range(60)]
	seconds = [str(val).zfill(2) for val in range(60)]

	# Build lits of first names and last names	
	fnames = open(first_name_file).readlines()
	fnames = [fname.lower().strip() for fname in fnames]
	lnames = open(last_name_file).readlines()
	lnames = [lname.lower().strip() for lname in lnames]
	
    mobile_start_digists = [7, 8, 9]
	lead_count = 0	
	is_completed = False
	while True:
		batch_leads = []
		for lead_index in range(batch_size):
			# Prepare random values for basic fields
			fname = random.choice(fnames)
			lname = random.choice(lnames)
			email_domain = random.choice(email_domains)
			email = "%s%s@%s" % (fname, lname, email_domain)
			_mobile_digits = random.randint(10**8, 10**9-1) 		
			mobile = "%s%s" % (random.choice(mobile_start_digists), _mobile_digits)
			badgeID = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		
			lead_fields = []
			lead_fields.append({'fieldName': 'firstName', 'fieldValue': fname})
			lead_fields.append({'fieldName': 'lastName', 'fieldValue': lname})
			lead_fields.append({'fieldName': 'email', 'fieldValue': email})
			lead_fields.append({'fieldName': 'contactNo', 'fieldValue': mobile})
			lead_fields.append({'fieldName': 'badgeID', 'fieldValue': badgeID})
			lead_fields.append({'fieldName': 'badgeData', 'fieldValue': ""})
			# Generate the user selected answers
			lead_answers = []
			selected_answers = dict()
			for questionID in question_answers:
				values = question_answers[questionID]
				value = random.choice(values)
				selected_answers[questionID] = value
			# Get the capture time
			capture_time = "%s %s:%s:%s" % (exhibition_date, random.choice(hours), random.choice(minutes), random.choice(seconds))
			# Build the lead information
			lead_info = {}			
			lead_info['captureTime'] = capture_time
			lead_info['leadFields'] = lead_fields			
			lead_info['selectedAnswers'] = selected_answers			
			batch_leads.append(lead_info)

		time_interval = 0 # Interval for visits across exhibitors
		for exhibitor in exhibitors:
			exhibitorID, exhibitor_name, user_name = exhibitor
			# Get the qualifier questions
			questions = qualifier_questions[exhibitor_name]
			leads = []
			# Process batch leads
			for batch_lead in batch_leads:
				lead_count += 1
				lead_info = {}
				# Prepare the capture time
				capture_time = batch_lead['captureTime']
				capture_time_obj = datetime.strptime(capture_time, tradeshow_time_fromat)
				capture_time_obj = capture_time_obj + timedelta(minutes=time_interval)
				lead_info['captureTime'] = datetime.strftime(capture_time_obj, tradeshow_time_fromat)
				# generate leadID , this will be new for each visit of a lead to the exhibitors
				_leadID = fname + lead_info['captureTime']
				leadID = hashlib.md5(_leadID).hexdigest()
				# Prepare lead info
				lead_info['leadID'] = leadID
				lead_info['leadType'] = random.choice(lead_types)
				lead_info['scanType'] = random.choice(scan_types)
				lead_info['lookupStatus'] = ''
				lead_info['leadSyncStatus'] = '0'
				lead_info['syncID'] = '0'
				lead_info['leadFields'] = batch_lead['leadFields'] 		
				selected_answers = batch_lead['selectedAnswers']
				lead_answers = []
				# Prepare the lead question answers
				for question in questions:
					answer = {}
					org_questionID, qualifier_questionID = question
					answer = {'qualifierQuestionID': qualifier_questionID, 'answerValue': selected_answers[org_questionID]}
					lead_answers.append(answer)
				lead_info['leadAnswers'] = lead_answers
				leads.append(lead_info)
				if lead_count >= lead_generation_count:
					break
			leads_request = {}
			leads_request['exhibitorID'] = exhibitorID
			leads_request['tradeshowID'] = tradeshowID
			leads_request['userName'] = user_name
			leads_request['leads'] = leads
			#pprint(leads_request)
			response = requests.post(upload_api, data=json.dumps(leads_request))
			print response.text
			# Trigger lead uplaod					
			
			time_interval += 10
			if lead_count >= lead_generation_count:
				is_completed = True
				break
		
		if is_completed:
			break			

if __name__ == "__main__":
	main()
