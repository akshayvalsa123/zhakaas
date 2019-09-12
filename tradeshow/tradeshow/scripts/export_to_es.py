from datetime import datetime
import json
import requests

from elasticsearch import Elasticsearch

api = "http://localhost:8088/api/get/report?tradeshowID=2&amp;exhibitorID=all"
es_host = "localhost:9200"
tradeshow_time_format = "%Y-%m-%d %H:%M:%S"

def main():
	"""
	"""
	_response = requests.get(api)
	response = json.loads(_response.text)
	exhibitorLeads = response['response']['exhibitorLeads']
	tradeshow = response['response']['tradeshow']
	_tradeshow = tradeshow.replace(' ', '_').lower()
	today = datetime.today()	
	#index_name = "%s-%s-%s_%s" % (today.year, today.month, today.day, _tradeshow)
	index_name = "2017-09-03_%s" % _tradeshow
	print "Index Name: %s" % index_name	
	es = Elasticsearch([es_host])
	es.indices.delete(index=index_name, ignore=[400, 404])
	es.indices.create(index=index_name, ignore=400)	
	total_lead_count = 0
	for exhibitorLead in exhibitorLeads:
		leads = exhibitorLead['leads']
		exhibitor = exhibitorLead['exhibitor']
		doc_type = exhibitor.replace(' ', '_').upper()
		lead_count = 0
		for lead in leads:
			lead_count += 1
			total_lead_count += 1
			captureTime = datetime.strptime(lead['captureTime'], tradeshow_time_format)
			lead['captureTime'] = captureTime			
			result = es.index(index_name, doc_type, body=lead)
		print "Exhibitor: %s, LeadCount: [%s]" % (exhibitor, lead_count)
	print "Total Leads: [%s]" % total_lead_count

if __name__ == "__main__":
	main()
